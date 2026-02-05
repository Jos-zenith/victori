import { ref, onUnmounted, computed } from 'vue'
import type { SensorData, DeviceStatus, SensorHistoryPoint } from '../types'
import { generateSimulatedSensorData } from '../utils/carbon-calculations'

/**
 * Composable for managing real-time ESP32 sensor connections.
 *
 * Supports two modes:
 *  1. WebSocket (ws://ESP32_IP/ws) - for direct local connection
 *  2. HTTP Polling (http://ESP32_IP/api/sensors) - fallback mode
 *
 * When ESP32 is not available, falls back to simulated data for demo.
 */
export function useESP32Connection() {
  // Connection state
  const isConnected = ref(false)
  const connectionMode = ref<'websocket' | 'polling' | 'simulated'>('simulated')
  const esp32Ip = ref('192.168.1.100')
  const esp32Port = ref(81)
  const pollingInterval = ref(3000) // 3 seconds

  // Sensor data
  const currentSensorData = ref<SensorData>(generateSimulatedSensorData())
  const sensorHistory = ref<SensorHistoryPoint[]>([])
  const maxHistoryPoints = 60

  // Device status
  const deviceStatus = ref<DeviceStatus>({
    id: 'esp32-001',
    name: 'HCCMS Sensor Hub',
    status: 'offline',
    lastHeartbeat: new Date().toISOString(),
    batteryLevel: 100,
    firmwareVersion: '2.1.0',
    sensors: ['DHT11', 'Soil Moisture', 'pH', 'LDR', 'MQ135', 'ESP32-CAM'],
  })

  // Internal refs
  let ws: WebSocket | null = null
  let pollTimer: ReturnType<typeof setInterval> | null = null
  let simTimer: ReturnType<typeof setInterval> | null = null

  // Connection error
  const connectionError = ref('')

  const wsUrl = computed(() => `ws://${esp32Ip.value}:${esp32Port.value}/ws`)
  const httpUrl = computed(() => `http://${esp32Ip.value}/api/sensors`)

  // ==================== DATA PROCESSING ====================

  function processSensorData(data: SensorData) {
    currentSensorData.value = { ...data, timestamp: new Date().toISOString() }

    // Add to history
    const point: SensorHistoryPoint = {
      time: new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      temperature: Math.round(data.temperature * 10) / 10,
      humidity: Math.round(data.humidity * 10) / 10,
      co2Emitted: Math.round(data.co2Emitted * 10) / 10,
      co2Absorbed: Math.round(data.co2Absorbed * 10) / 10,
      o2Released: Math.round(data.o2Released * 10) / 10,
      soilMoisture: Math.round(data.soilMoisture * 10) / 10,
      lightIntensity: Math.round(data.lightIntensity * 10) / 10,
    }

    sensorHistory.value = [...sensorHistory.value.slice(-(maxHistoryPoints - 1)), point]

    // Update device heartbeat
    deviceStatus.value.lastHeartbeat = new Date().toISOString()
  }

  // ==================== WEBSOCKET CONNECTION ====================

  function connectWebSocket() {
    disconnectAll()
    connectionError.value = ''

    try {
      ws = new WebSocket(wsUrl.value)

      ws.onopen = () => {
        isConnected.value = true
        connectionMode.value = 'websocket'
        deviceStatus.value.status = 'online'
        connectionError.value = ''
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          if (msg.type === 'sensor_data' && msg.payload) {
            processSensorData(msg.payload as SensorData)
          } else if (msg.type === 'heartbeat') {
            deviceStatus.value.lastHeartbeat = new Date().toISOString()
            deviceStatus.value.batteryLevel = msg.payload?.battery ?? 100
          }
        } catch {
          // Non-JSON message, try parsing as raw sensor data
          try {
            const data = JSON.parse(event.data)
            if (data.temperature !== undefined) {
              processSensorData(data as SensorData)
            }
          } catch {
            // Ignore unparseable messages
          }
        }
      }

      ws.onclose = () => {
        isConnected.value = false
        deviceStatus.value.status = 'offline'
        connectionError.value = 'WebSocket connection closed. Retrying...'
        // Auto-retry after 5 seconds
        setTimeout(() => {
          if (connectionMode.value === 'websocket') {
            connectWebSocket()
          }
        }, 5000)
      }

      ws.onerror = () => {
        connectionError.value = 'WebSocket connection failed. Falling back to HTTP polling...'
        ws?.close()
        // Fallback to polling
        connectHTTPPolling()
      }
    } catch {
      connectionError.value = 'Failed to create WebSocket. Falling back to HTTP polling...'
      connectHTTPPolling()
    }
  }

  // ==================== HTTP POLLING ====================

  function connectHTTPPolling() {
    disconnectAll()
    connectionError.value = ''
    connectionMode.value = 'polling'

    async function poll() {
      try {
        const response = await fetch(httpUrl.value, {
          signal: AbortSignal.timeout(5000),
        })
        if (!response.ok) throw new Error('HTTP error')
        const data = await response.json()
        processSensorData(data as SensorData)
        isConnected.value = true
        deviceStatus.value.status = 'online'
        connectionError.value = ''
      } catch {
        isConnected.value = false
        deviceStatus.value.status = 'error'
        connectionError.value = 'Cannot reach ESP32. Using simulated data.'
        // Fallback to simulated
        startSimulation()
      }
    }

    poll()
    pollTimer = setInterval(poll, pollingInterval.value)
  }

  // ==================== SIMULATED MODE ====================

  function startSimulation() {
    disconnectAll()
    connectionMode.value = 'simulated'
    isConnected.value = false
    deviceStatus.value.status = 'offline'
    connectionError.value = ''

    function tick() {
      processSensorData(generateSimulatedSensorData())
    }

    tick()
    simTimer = setInterval(tick, pollingInterval.value)
  }

  // ==================== CONNECTION MANAGEMENT ====================

  function disconnectAll() {
    if (ws) {
      ws.onclose = null // prevent auto-retry
      ws.close()
      ws = null
    }
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
    if (simTimer) {
      clearInterval(simTimer)
      simTimer = null
    }
  }

  function connect(mode: 'websocket' | 'polling' | 'simulated' = 'websocket') {
    switch (mode) {
      case 'websocket':
        connectWebSocket()
        break
      case 'polling':
        connectHTTPPolling()
        break
      case 'simulated':
        startSimulation()
        break
    }
  }

  function disconnect() {
    disconnectAll()
    isConnected.value = false
    connectionMode.value = 'simulated'
    deviceStatus.value.status = 'offline'
  }

  function updateConfig(ip: string, port: number = 81) {
    esp32Ip.value = ip
    esp32Port.value = port
  }

  // Cleanup on unmount
  onUnmounted(() => {
    disconnectAll()
  })

  // Start with simulated data by default
  startSimulation()

  return {
    // State
    isConnected,
    connectionMode,
    connectionError,
    currentSensorData,
    sensorHistory,
    deviceStatus,
    esp32Ip,
    esp32Port,

    // Methods
    connect,
    disconnect,
    updateConfig,
    startSimulation,
  }
}
