<script setup lang="ts">
import { computed } from 'vue'
import type { CarbonCreditScore } from '../types'

const props = defineProps<{
  score: CarbonCreditScore
}>()

const scoreColor = computed(() => {
  const s = props.score.totalScore
  if (s >= 80) return '#16a34a'
  if (s >= 60) return '#65a30d'
  if (s >= 40) return '#ea580c'
  return '#dc2626'
})

const gradeColor = computed(() => {
  const g = props.score.grade
  if (g === 'A+' || g === 'A') return '#16a34a'
  if (g === 'B+' || g === 'B') return '#65a30d'
  if (g === 'C') return '#ea580c'
  return '#dc2626'
})

const circumference = 2 * Math.PI * 54
const dashOffset = computed(() => {
  return circumference - (props.score.totalScore / 100) * circumference
})
</script>

<template>
  <div class="score-card">
    <div class="score-header">
      <h3>Carbon Credit Score</h3>
      <span class="live-badge">LIVE</span>
    </div>

    <div class="score-body">
      <!-- Circular Score Display -->
      <div class="score-circle-container">
        <svg class="score-svg" viewBox="0 0 120 120">
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke="#e2e8f0"
            stroke-width="8"
          />
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            :stroke="scoreColor"
            stroke-width="8"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
            transform="rotate(-90 60 60)"
            class="score-ring"
          />
        </svg>
        <div class="score-inner">
          <div class="score-number" :style="{ color: scoreColor }">{{ score.totalScore }}</div>
          <div class="score-of">/100</div>
        </div>
      </div>

      <!-- Grade Badge -->
      <div class="grade-badge" :style="{ background: gradeColor }">
        Grade {{ score.grade }}
      </div>

      <!-- Breakdown -->
      <div class="breakdown-grid">
        <div class="breakdown-item">
          <div class="breakdown-label">Sequestration</div>
          <div class="breakdown-bar">
            <div class="breakdown-fill" :style="{ width: score.breakdown.sequestrationScore + '%', background: '#16a34a' }"></div>
          </div>
          <div class="breakdown-value">{{ score.breakdown.sequestrationScore }}%</div>
        </div>
        <div class="breakdown-item">
          <div class="breakdown-label">Emission Offset</div>
          <div class="breakdown-bar">
            <div class="breakdown-fill" :style="{ width: score.breakdown.emissionOffset + '%', background: '#0284c7' }"></div>
          </div>
          <div class="breakdown-value">{{ score.breakdown.emissionOffset }}%</div>
        </div>
        <div class="breakdown-item">
          <div class="breakdown-label">Env. Health</div>
          <div class="breakdown-bar">
            <div class="breakdown-fill" :style="{ width: score.breakdown.environmentalHealth + '%', background: '#7c3aed' }"></div>
          </div>
          <div class="breakdown-value">{{ score.breakdown.environmentalHealth }}%</div>
        </div>
        <div class="breakdown-item">
          <div class="breakdown-label">O2 Production</div>
          <div class="breakdown-bar">
            <div class="breakdown-fill" :style="{ width: score.breakdown.oxygenProduction + '%', background: '#0891b2' }"></div>
          </div>
          <div class="breakdown-value">{{ score.breakdown.oxygenProduction }}%</div>
        </div>
      </div>

      <!-- Credits Summary -->
      <div class="credits-row">
        <div class="credit-item">
          <span class="credit-label">Credits Earned</span>
          <span class="credit-value">{{ score.creditsEarned.toFixed(4) }}</span>
        </div>
        <div class="credit-item">
          <span class="credit-label">Value (USD)</span>
          <span class="credit-value credit-usd">${{ score.creditValueUSD.toFixed(2) }}</span>
        </div>
        <div class="credit-item">
          <span class="credit-label">Net CO2 Balance</span>
          <span class="credit-value" :class="{ positive: score.netCarbonBalance > 0, negative: score.netCarbonBalance < 0 }">
            {{ score.netCarbonBalance > 0 ? '+' : '' }}{{ score.netCarbonBalance.toFixed(1) }} ppm
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.score-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e8eef7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.score-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1e293b;
}

.live-badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  background: #dc2626;
  color: white;
  letter-spacing: 1px;
  animation: pulse-live 2s infinite;
}

@keyframes pulse-live {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.score-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.score-circle-container {
  position: relative;
  width: 140px;
  height: 140px;
}

.score-svg {
  width: 100%;
  height: 100%;
}

.score-ring {
  transition: stroke-dashoffset 0.8s ease;
}

.score-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-number {
  font-size: 2.4rem;
  font-weight: 800;
  line-height: 1;
}

.score-of {
  font-size: 0.8rem;
  color: #94a3b8;
  font-weight: 500;
}

.grade-badge {
  color: white;
  font-size: 0.85rem;
  font-weight: 700;
  padding: 6px 24px;
  border-radius: 20px;
  letter-spacing: 0.5px;
}

.breakdown-grid {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.breakdown-label {
  width: 110px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  flex-shrink: 0;
}

.breakdown-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.breakdown-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease;
}

.breakdown-value {
  width: 40px;
  text-align: right;
  font-size: 0.75rem;
  font-weight: 700;
  color: #475569;
}

.credits-row {
  width: 100%;
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.credit-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.credit-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.credit-value {
  font-size: 0.95rem;
  font-weight: 700;
  color: #1e293b;
}

.credit-usd {
  color: #16a34a;
}

.positive {
  color: #16a34a;
}

.negative {
  color: #dc2626;
}
</style>
