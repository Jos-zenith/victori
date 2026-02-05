<script setup lang="ts">
import { ref } from 'vue'
import type { DeviceStatus } from '../types'

const props = defineProps<{
  isConnected: boolean
  connectionMode: 'websocket' | 'polling' | 'simulated'
  connectionError: string
  deviceStatus: DeviceStatus
  esp32Ip: string
}>()

const emit = defineEmits<{
  connect: [mode: 'websocket' | 'polling' | 'simulated']
  disconnect: []
  updateIp: [ip: string]
}>()

const inputIp = ref(props.esp32Ip)
const showConfig = ref(false)

function handleConnect(mode: 'websocket' | 'polling' | 'simulated') {
  if (inputIp.value && inputIp.value !== props.esp32Ip) {
    emit('updateIp', inputIp.value)
  }
  emit('connect', mode)
}
</script>

<template>
  <div class="connection-panel">
    <div class="conn-header">
      <div class="conn-title-row">
        <h3>ESP32 Connection</h3>
        <div
          class="status-dot"
          :class="{
            online: isConnected,
            offline: !isConnected && connectionMode === 'simulated',
            error: !isConnected && connectionMode !== 'simulated',
          }"
        ></div>
      </div>
      <button class="config-toggle" @click="showConfig = !showConfig">
        {{ showConfig ? 'Hide' : 'Configure' }}
      </button>
    </div>

    <!-- Status Row -->
    <div class="status-row">
      <div class="status-chip" :class="connectionMode">
        {{ connectionMode === 'websocket' ? 'WebSocket' : connectionMode === 'polling' ? 'HTTP Poll' : 'Simulated' }}
      </div>
      <span class="device-name">{{ deviceStatus.name }}</span>
    </div>

    <!-- Error -->
    <div v-if="connectionError" class="conn-error">
      {{ connectionError }}
    </div>

    <!-- Config Panel -->
    <div v-if="showConfig" class="config-section">
      <div class="config-field">
        <label>ESP32 IP Address</label>
        <input
          v-model="inputIp"
          type="text"
          placeholder="192.168.1.100"
          class="config-input"
        />
      </div>

      <div class="config-actions">
        <button class="conn-btn ws" @click="handleConnect('websocket')">
          WebSocket
        </button>
        <button class="conn-btn http" @click="handleConnect('polling')">
          HTTP Poll
        </button>
        <button class="conn-btn sim" @click="handleConnect('simulated')">
          Simulate
        </button>
      </div>

      <button
        v-if="isConnected"
        class="disconnect-btn"
        @click="$emit('disconnect')"
      >
        Disconnect
      </button>
    </div>

    <!-- Device Info -->
    <div class="device-info">
      <div class="info-item">
        <span class="info-label">Status</span>
        <span class="info-value" :class="deviceStatus.status">{{ deviceStatus.status }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">Battery</span>
        <span class="info-value">{{ deviceStatus.batteryLevel }}%</span>
      </div>
      <div class="info-item">
        <span class="info-label">Firmware</span>
        <span class="info-value">v{{ deviceStatus.firmwareVersion }}</span>
      </div>
    </div>

    <!-- Sensor List -->
    <div class="sensor-chips">
      <span v-for="s in deviceStatus.sensors" :key="s" class="sensor-chip">{{ s }}</span>
    </div>
  </div>
</template>

<style scoped>
.connection-panel {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e8eef7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.conn-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.conn-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.conn-title-row h3 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e293b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #16a34a;
  box-shadow: 0 0 6px #16a34a80;
}

.status-dot.offline {
  background: #94a3b8;
}

.status-dot.error {
  background: #dc2626;
  box-shadow: 0 0 6px #dc262680;
}

.config-toggle {
  font-size: 0.75rem;
  font-weight: 600;
  color: #0284c7;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
}

.config-toggle:hover {
  opacity: 0.8;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.status-chip {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-chip.websocket {
  background: #16a34a14;
  color: #16a34a;
}

.status-chip.polling {
  background: #0284c714;
  color: #0284c7;
}

.status-chip.simulated {
  background: #ea580c14;
  color: #ea580c;
}

.device-name {
  font-size: 0.8rem;
  color: #64748b;
}

.conn-error {
  font-size: 0.75rem;
  color: #dc2626;
  background: #fef2f2;
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 10px;
  border-left: 3px solid #dc2626;
}

.config-section {
  padding: 14px;
  background: #f8fafc;
  border-radius: 10px;
  margin-bottom: 12px;
}

.config-field {
  margin-bottom: 12px;
}

.config-field label {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 4px;
}

.config-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.85rem;
  color: #1e293b;
  background: #ffffff;
  outline: none;
  transition: border-color 0.2s;
}

.config-input:focus {
  border-color: #0284c7;
}

.config-actions {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.conn-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
}

.conn-btn.ws {
  background: #16a34a;
}

.conn-btn.http {
  background: #0284c7;
}

.conn-btn.sim {
  background: #ea580c;
}

.conn-btn:hover {
  transform: translateY(-1px);
  opacity: 0.9;
}

.disconnect-btn {
  width: 100%;
  padding: 8px;
  border: 1px solid #dc2626;
  border-radius: 6px;
  background: transparent;
  color: #dc2626;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.disconnect-btn:hover {
  background: #fef2f2;
}

.device-info {
  display: flex;
  gap: 16px;
  padding: 10px 0;
  border-top: 1px solid #f1f5f9;
  margin-top: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 0.6rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.info-value {
  font-size: 0.8rem;
  font-weight: 700;
  color: #1e293b;
}

.info-value.online {
  color: #16a34a;
}

.info-value.offline {
  color: #94a3b8;
}

.info-value.error {
  color: #dc2626;
}

.sensor-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 10px;
}

.sensor-chip {
  font-size: 0.6rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 8px;
  background: #f1f5f9;
  color: #475569;
}
</style>
