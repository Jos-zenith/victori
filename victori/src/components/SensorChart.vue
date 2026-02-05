<script setup lang="ts">
import { computed, ref } from 'vue'
import type { SensorHistoryPoint } from '../types'

const props = defineProps<{
  history: SensorHistoryPoint[]
}>()

const activeMetric = ref<'temperature' | 'humidity' | 'co2Emitted' | 'co2Absorbed' | 'o2Released' | 'soilMoisture' | 'lightIntensity'>('temperature')

const metrics = [
  { key: 'temperature' as const, label: 'Temp', unit: '\u00B0C', color: '#dc2626' },
  { key: 'humidity' as const, label: 'Humidity', unit: '%', color: '#0284c7' },
  { key: 'co2Emitted' as const, label: 'CO\u2082 Emitted', unit: 'ppm', color: '#ea580c' },
  { key: 'co2Absorbed' as const, label: 'CO\u2082 Absorbed', unit: 'ppm', color: '#16a34a' },
  { key: 'o2Released' as const, label: 'O\u2082 Released', unit: 'ppm', color: '#7c3aed' },
  { key: 'soilMoisture' as const, label: 'Soil', unit: '%', color: '#854d0e' },
  { key: 'lightIntensity' as const, label: 'Light', unit: '\u00B5mol', color: '#ca8a04' },
]

const currentMetric = computed(() => metrics.find(m => m.key === activeMetric.value)!)

const chartData = computed(() => {
  const data = props.history
  if (data.length === 0) return { points: '', min: 0, max: 100, values: [] }

  const values = data.map(d => d[activeMetric.value])
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1

  const width = 600
  const height = 150
  const padding = 10

  const points = data.map((d, i) => {
    const x = padding + (i / Math.max(data.length - 1, 1)) * (width - 2 * padding)
    const y = height - padding - ((d[activeMetric.value] - min) / range) * (height - 2 * padding)
    return `${x},${y}`
  }).join(' ')

  // Area fill path
  const firstX = padding
  const lastX = padding + ((data.length - 1) / Math.max(data.length - 1, 1)) * (width - 2 * padding)
  const areaPath = `M ${firstX},${height - padding} L ${points.split(' ').map(p => `L ${p}`).join(' ')} L ${lastX},${height - padding} Z`

  return { points, areaPath, min: min.toFixed(1), max: max.toFixed(1), values }
})

const latestValue = computed(() => {
  if (props.history.length === 0) return '--'
  const last = props.history[props.history.length - 1]
  return last[activeMetric.value].toFixed(1)
})
</script>

<template>
  <div class="chart-panel">
    <div class="chart-header">
      <div>
        <h3>Real-Time Sensor Data</h3>
        <div class="chart-latest">
          <span class="latest-value" :style="{ color: currentMetric.color }">{{ latestValue }}</span>
          <span class="latest-unit">{{ currentMetric.unit }}</span>
        </div>
      </div>
      <span class="chart-count">{{ history.length }} readings</span>
    </div>

    <!-- Metric Tabs -->
    <div class="metric-tabs">
      <button
        v-for="m in metrics"
        :key="m.key"
        class="metric-tab"
        :class="{ active: activeMetric === m.key }"
        :style="activeMetric === m.key ? { background: m.color + '14', color: m.color, borderColor: m.color } : {}"
        @click="activeMetric = m.key"
      >
        {{ m.label }}
      </button>
    </div>

    <!-- SVG Chart -->
    <div class="chart-container">
      <svg viewBox="0 0 600 150" class="chart-svg" v-if="history.length > 1">
        <!-- Grid lines -->
        <line x1="10" y1="10" x2="10" y2="140" stroke="#f1f5f9" stroke-width="1"/>
        <line x1="10" y1="140" x2="590" y2="140" stroke="#f1f5f9" stroke-width="1"/>
        <line x1="10" y1="75" x2="590" y2="75" stroke="#f1f5f9" stroke-width="0.5" stroke-dasharray="4"/>

        <!-- Area fill -->
        <path
          :d="chartData.areaPath"
          :fill="currentMetric.color"
          fill-opacity="0.08"
        />

        <!-- Line -->
        <polyline
          :points="chartData.points"
          fill="none"
          :stroke="currentMetric.color"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />

        <!-- Y-axis labels -->
        <text x="14" y="18" class="axis-label">{{ chartData.max }}</text>
        <text x="14" y="138" class="axis-label">{{ chartData.min }}</text>
      </svg>

      <div v-else class="chart-placeholder">
        Collecting data...
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-panel {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e8eef7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
}

.chart-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.chart-latest {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.latest-value {
  font-size: 1.8rem;
  font-weight: 800;
}

.latest-unit {
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 500;
}

.chart-count {
  font-size: 0.7rem;
  font-weight: 600;
  color: #94a3b8;
  padding: 3px 10px;
  background: #f8fafc;
  border-radius: 10px;
}

.metric-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 14px;
}

.metric-tab {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.metric-tab:hover {
  background: #f1f5f9;
}

.metric-tab.active {
  border-width: 1.5px;
}

.chart-container {
  width: 100%;
  overflow: hidden;
}

.chart-svg {
  width: 100%;
  height: auto;
}

.axis-label {
  font-size: 9px;
  fill: #94a3b8;
  font-family: sans-serif;
}

.chart-placeholder {
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 0.85rem;
}
</style>
