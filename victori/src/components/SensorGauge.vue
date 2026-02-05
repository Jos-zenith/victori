<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: number
  unit: string
  min: number
  max: number
  optimalMin: number
  optimalMax: number
  icon: string
  color: string
}>()

const percentage = computed(() => {
  const range = props.max - props.min
  return Math.max(0, Math.min(100, ((props.value - props.min) / range) * 100))
})

const isOptimal = computed(() => {
  return props.value >= props.optimalMin && props.value <= props.optimalMax
})

const statusText = computed(() => {
  if (props.value < props.optimalMin) return 'Low'
  if (props.value > props.optimalMax) return 'High'
  return 'Optimal'
})

const displayValue = computed(() => {
  return Math.round(props.value * 10) / 10
})
</script>

<template>
  <div class="sensor-gauge" :class="{ optimal: isOptimal }">
    <div class="gauge-header">
      <span class="gauge-icon">{{ icon }}</span>
      <span class="gauge-label">{{ label }}</span>
    </div>
    <div class="gauge-value" :style="{ color: color }">
      {{ displayValue }}<span class="gauge-unit">{{ unit }}</span>
    </div>
    <div class="gauge-bar-track">
      <div
        class="gauge-bar-fill"
        :style="{ width: percentage + '%', background: color }"
      ></div>
      <div
        class="gauge-optimal-zone"
        :style="{
          left: ((optimalMin - min) / (max - min)) * 100 + '%',
          width: ((optimalMax - optimalMin) / (max - min)) * 100 + '%',
        }"
      ></div>
    </div>
    <div class="gauge-footer">
      <span class="gauge-range">{{ min }}{{ unit }}</span>
      <span class="gauge-status" :class="statusText.toLowerCase()">{{ statusText }}</span>
      <span class="gauge-range">{{ max }}{{ unit }}</span>
    </div>
  </div>
</template>

<style scoped>
.sensor-gauge {
  background: #ffffff;
  border-radius: 12px;
  padding: 18px;
  border: 1px solid #e8eef7;
  transition: all 0.3s ease;
}

.sensor-gauge:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.sensor-gauge.optimal {
  border-color: #16a34a33;
}

.gauge-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.gauge-icon {
  font-size: 1.2rem;
}

.gauge-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.gauge-value {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 12px;
}

.gauge-unit {
  font-size: 0.9rem;
  font-weight: 500;
  opacity: 0.7;
  margin-left: 2px;
}

.gauge-bar-track {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  position: relative;
  overflow: hidden;
  margin-bottom: 8px;
}

.gauge-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.gauge-optimal-zone {
  position: absolute;
  top: -2px;
  height: 10px;
  border: 1.5px solid #16a34a;
  border-radius: 5px;
  background: transparent;
  pointer-events: none;
}

.gauge-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.gauge-range {
  font-size: 0.7rem;
  color: #94a3b8;
}

.gauge-status {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 2px 8px;
  border-radius: 10px;
}

.gauge-status.optimal {
  color: #16a34a;
  background: #16a34a14;
}

.gauge-status.low {
  color: #ea580c;
  background: #ea580c14;
}

.gauge-status.high {
  color: #dc2626;
  background: #dc262614;
}
</style>
