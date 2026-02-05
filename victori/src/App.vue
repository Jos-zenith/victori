<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import SensorGauge from './components/SensorGauge.vue'
import CarbonScoreCard from './components/CarbonScoreCard.vue'
import ChaveAnalysisPanel from './components/ChaveAnalysisPanel.vue'
import ConnectionPanel from './components/ConnectionPanel.vue'
import SensorChart from './components/SensorChart.vue'
import TreeIdentifier from './components/TreeIdentifier.vue'
import { useESP32Connection } from './composables/useESP32Connection'
import {
  TREE_SPECIES_DB,
  calculateChaveResult,
  calculateCarbonCreditScore,
} from './utils/carbon-calculations'
import type { TreeSpecies, ChaveResult, CarbonCreditScore, TreeIdentificationResult } from './types'

// ==================== NAVIGATION ====================
const sidebarOpen = ref(true)
const currentPage = ref('dashboard')

const navItems = [
  { key: 'dashboard', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { key: 'calculator', label: 'Carbon Calculator', icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z' },
  { key: 'sensors', label: 'Live Sensors', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
  { key: 'identify', label: 'Identify Trees', icon: 'M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z' },
  { key: 'history', label: 'History', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
]

// ==================== ESP32 CONNECTION ====================
const {
  isConnected,
  connectionMode,
  connectionError,
  currentSensorData,
  sensorHistory,
  deviceStatus,
  esp32Ip,
  connect,
  disconnect,
  updateConfig,
  startSimulation,
} = useESP32Connection()

// ==================== TREE & CHAVE STATE ====================
const selectedSpeciesKey = ref('mango')
const selectedSpecies = computed<TreeSpecies>(() => {
  return TREE_SPECIES_DB[selectedSpeciesKey.value] || TREE_SPECIES_DB['mango']
})
const chaveResult = computed<ChaveResult>(() => calculateChaveResult(selectedSpecies.value))

// ==================== CARBON CREDIT SCORE ====================
const carbonScore = computed<CarbonCreditScore>(() =>
  calculateCarbonCreditScore(currentSensorData.value, selectedSpecies.value)
)

// ==================== DASHBOARD METRICS ====================
const totalTrees = ref(5)
const totalCO2Offset = ref(2450.8)
const monthlyTarget = ref(500)
const currentMonth = ref(245.5)

// ==================== IDENTIFICATION HISTORY ====================
const identificationHistory = ref<Array<{
  id: number
  species: string
  confidence: number
  date: string
  credits: number
}>>([
  { id: 1, species: 'Mango Tree', confidence: 94, date: '2 hours ago', credits: 0.1284 },
  { id: 2, species: 'Coconut Tree', confidence: 89, date: '5 hours ago', credits: 0.0891 },
  { id: 3, species: 'Neem Tree', confidence: 91, date: '1 day ago', credits: 0.2310 },
])

function handleTreeIdentified(result: TreeIdentificationResult) {
  identificationHistory.value.unshift({
    id: identificationHistory.value.length + 1,
    species: result.species,
    confidence: result.confidence,
    date: 'Just now',
    credits: result.chaveResult.carbonCredits,
  })
  totalTrees.value++
}

function handleSpeciesSelected(species: TreeSpecies) {
  const key = Object.keys(TREE_SPECIES_DB).find(
    k => TREE_SPECIES_DB[k].name === species.name
  )
  if (key) selectedSpeciesKey.value = key
}

function handleConnect(mode: 'websocket' | 'polling' | 'simulated') {
  connect(mode)
}

function handleUpdateIp(ip: string) {
  updateConfig(ip)
}

// Update dashboard metrics when score changes
watch(carbonScore, (score) => {
  if (score.creditsEarned > 0) {
    totalCO2Offset.value = Math.round((totalCO2Offset.value + score.creditsEarned * 0.01) * 100) / 100
    currentMonth.value = Math.round((currentMonth.value + score.creditsEarned * 0.001) * 100) / 100
  }
})

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    dashboard: 'Dashboard',
    calculator: 'Carbon Credit Score Calculator',
    sensors: 'Live Sensor Monitoring',
    identify: 'Tree Bark Identification',
    history: 'Identification History',
  }
  return titles[currentPage.value] || 'Dashboard'
})
</script>

<template>
  <div class="saas-app">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: !sidebarOpen }">
      <div class="sidebar-header">
        <div class="logo">
          <svg class="logo-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 22c4-4 8-7.5 8-12a8 8 0 10-16 0c0 4.5 4 8 8 12z"/>
            <path d="M12 12V8M12 12l3 3M12 12l-3 3"/>
          </svg>
          <span class="logo-text" v-if="sidebarOpen">Victori</span>
        </div>
        <button class="toggle-btn" @click="sidebarOpen = !sidebarOpen">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
          </svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="item in navItems"
          :key="item.key"
          @click="currentPage = item.key"
          class="nav-item"
          :class="{ active: currentPage === item.key }"
        >
          <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path :d="item.icon"/>
          </svg>
          <span class="nav-label" v-if="sidebarOpen">{{ item.label }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <div class="connection-mini" v-if="sidebarOpen">
          <div class="mini-dot" :class="{ online: isConnected }"></div>
          <span>{{ isConnected ? 'Connected' : 'Simulated' }}</span>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content" :class="{ 'sidebar-collapsed': !sidebarOpen }">
      <!-- Header -->
      <header class="top-header">
        <div class="header-content">
          <div class="header-left">
            <h1>{{ pageTitle }}</h1>
            <span class="header-badge" v-if="currentPage === 'calculator' || currentPage === 'sensors'">
              <span class="pulse-dot"></span>
              LIVE
            </span>
          </div>
          <div class="header-right">
            <div class="score-mini" v-if="carbonScore">
              <span class="score-mini-label">Score</span>
              <span class="score-mini-value" :class="'grade-' + carbonScore.grade.replace('+', 'plus')">{{ carbonScore.totalScore }}</span>
            </div>
          </div>
        </div>
      </header>

      <!-- ==================== DASHBOARD PAGE ==================== -->
      <section v-if="currentPage === 'dashboard'" class="page">
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-header">
              <h3>Total Trees</h3>
              <svg class="metric-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M12 22c4-4 8-7.5 8-12a8 8 0 10-16 0c0 4.5 4 8 8 12z"/></svg>
            </div>
            <div class="metric-value green">{{ totalTrees }}</div>
            <p class="metric-change positive">+1 this month</p>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <h3>Total CO2 Offset</h3>
              <svg class="metric-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#0284c7" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
            </div>
            <div class="metric-value blue">{{ totalCO2Offset }} kg</div>
            <p class="metric-change positive">12% from last month</p>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <h3>This Month</h3>
              <svg class="metric-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7c3aed" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            </div>
            <div class="metric-value purple">{{ currentMonth }} kg</div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: (currentMonth / monthlyTarget * 100) + '%' }"></div>
            </div>
            <p class="metric-target">Target: {{ monthlyTarget }} kg</p>
          </div>

          <div class="metric-card">
            <div class="metric-header">
              <h3>Carbon Score</h3>
              <svg class="metric-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2"><path d="M12 15l-2 5 9-11h-7l2-5-9 11h7z"/></svg>
            </div>
            <div class="metric-value orange">{{ carbonScore.grade }}</div>
            <p class="metric-change">{{ carbonScore.totalScore }}/100 points</p>
          </div>
        </div>

        <!-- Mini Sensor Readout & Recent IDs -->
        <div class="dashboard-grid">
          <div class="card">
            <div class="card-header">
              <h2>Live Environment</h2>
              <span class="card-badge" :class="connectionMode">{{ connectionMode }}</span>
            </div>
            <div class="mini-sensors">
              <div class="mini-sensor">
                <span class="ms-label">Temp</span>
                <span class="ms-value">{{ currentSensorData.temperature.toFixed(1) }}&deg;C</span>
              </div>
              <div class="mini-sensor">
                <span class="ms-label">Humidity</span>
                <span class="ms-value">{{ currentSensorData.humidity.toFixed(1) }}%</span>
              </div>
              <div class="mini-sensor">
                <span class="ms-label">CO2 Emitted</span>
                <span class="ms-value warn">{{ currentSensorData.co2Emitted.toFixed(0) }} ppm</span>
              </div>
              <div class="mini-sensor">
                <span class="ms-label">CO2 Absorbed</span>
                <span class="ms-value good">{{ currentSensorData.co2Absorbed.toFixed(0) }} ppm</span>
              </div>
              <div class="mini-sensor">
                <span class="ms-label">O2 Released</span>
                <span class="ms-value good">{{ currentSensorData.o2Released.toFixed(0) }} ppm</span>
              </div>
              <div class="mini-sensor">
                <span class="ms-label">Sunlight</span>
                <span class="ms-value">{{ currentSensorData.lightIntensity.toFixed(0) }} umol</span>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <h2>Recent Identifications</h2>
              <button class="btn-secondary" @click="currentPage = 'history'">View All</button>
            </div>
            <div class="recent-list">
              <div v-for="item in identificationHistory.slice(0, 4)" :key="item.id" class="recent-item">
                <div class="recent-icon-wrap">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2"><path d="M12 22c4-4 8-7.5 8-12a8 8 0 10-16 0c0 4.5 4 8 8 12z"/></svg>
                </div>
                <div class="recent-details">
                  <h4>{{ item.species }}</h4>
                  <p>{{ item.date }} &middot; {{ item.confidence }}% confidence</p>
                </div>
                <span class="badge">{{ item.credits.toFixed(4) }} cr</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ==================== CARBON CALCULATOR PAGE ==================== -->
      <section v-if="currentPage === 'calculator'" class="page">
        <div class="calculator-layout">
          <!-- Left Column: Sensor Gauges -->
          <div class="calc-sensors">
            <div class="sensor-gauges-grid">
              <SensorGauge
                label="Temperature"
                :value="currentSensorData.temperature"
                unit="&deg;C"
                :min="-10"
                :max="50"
                :optimal-min="20"
                :optimal-max="30"
                icon="T"
                color="#dc2626"
              />
              <SensorGauge
                label="Humidity"
                :value="currentSensorData.humidity"
                unit="%"
                :min="0"
                :max="100"
                :optimal-min="40"
                :optimal-max="80"
                icon="H"
                color="#0284c7"
              />
              <SensorGauge
                label="Sunlight"
                :value="currentSensorData.lightIntensity"
                unit=" umol/m2/s"
                :min="0"
                :max="1200"
                :optimal-min="400"
                :optimal-max="800"
                icon="S"
                color="#ca8a04"
              />
              <SensorGauge
                label="CO2 Emitted (Cars)"
                :value="currentSensorData.co2Emitted"
                unit=" ppm"
                :min="300"
                :max="600"
                :optimal-min="300"
                :optimal-max="400"
                icon="E"
                color="#ea580c"
              />
              <SensorGauge
                label="CO2 Absorbed (Trees)"
                :value="currentSensorData.co2Absorbed"
                unit=" ppm"
                :min="0"
                :max="600"
                :optimal-min="350"
                :optimal-max="600"
                icon="A"
                color="#16a34a"
              />
              <SensorGauge
                label="O2 Released (Trees)"
                :value="currentSensorData.o2Released"
                unit=" ppm"
                :min="0"
                :max="300"
                :optimal-min="150"
                :optimal-max="250"
                icon="O"
                color="#0891b2"
              />
            </div>

            <!-- Species Selector -->
            <div class="species-selector card-flat">
              <h4>Tree Species (for Chave Equation)</h4>
              <div class="species-options">
                <button
                  v-for="(species, key) in TREE_SPECIES_DB"
                  :key="key"
                  class="species-option"
                  :class="{ active: selectedSpeciesKey === key }"
                  @click="selectedSpeciesKey = key"
                >
                  {{ species.name }}
                </button>
              </div>
            </div>
          </div>

          <!-- Right Column: Score & Chave -->
          <div class="calc-results">
            <CarbonScoreCard :score="carbonScore" />
            <ChaveAnalysisPanel :species="selectedSpecies" :chave-result="chaveResult" />
          </div>
        </div>
      </section>

      <!-- ==================== LIVE SENSORS PAGE ==================== -->
      <section v-if="currentPage === 'sensors'" class="page">
        <div class="sensors-layout">
          <div class="sensors-main">
            <SensorChart :history="sensorHistory" />

            <div class="sensor-gauges-grid-full">
              <SensorGauge
                label="Temperature"
                :value="currentSensorData.temperature"
                unit="&deg;C"
                :min="-10"
                :max="50"
                :optimal-min="20"
                :optimal-max="30"
                icon="T"
                color="#dc2626"
              />
              <SensorGauge
                label="Humidity"
                :value="currentSensorData.humidity"
                unit="%"
                :min="0"
                :max="100"
                :optimal-min="40"
                :optimal-max="80"
                icon="H"
                color="#0284c7"
              />
              <SensorGauge
                label="Soil Moisture"
                :value="currentSensorData.soilMoisture"
                unit="%"
                :min="0"
                :max="100"
                :optimal-min="30"
                :optimal-max="70"
                icon="M"
                color="#854d0e"
              />
              <SensorGauge
                label="Sunlight (PAR)"
                :value="currentSensorData.lightIntensity"
                unit=" umol"
                :min="0"
                :max="1200"
                :optimal-min="400"
                :optimal-max="800"
                icon="L"
                color="#ca8a04"
              />
              <SensorGauge
                label="pH Level"
                :value="currentSensorData.ph"
                unit=""
                :min="0"
                :max="14"
                :optimal-min="5.5"
                :optimal-max="7.5"
                icon="pH"
                color="#7c3aed"
              />
              <SensorGauge
                label="CO2 Emitted (MQ135)"
                :value="currentSensorData.co2Emitted"
                unit=" ppm"
                :min="300"
                :max="600"
                :optimal-min="300"
                :optimal-max="400"
                icon="CO2"
                color="#ea580c"
              />
              <SensorGauge
                label="CO2 Absorbed"
                :value="currentSensorData.co2Absorbed"
                unit=" ppm"
                :min="0"
                :max="600"
                :optimal-min="350"
                :optimal-max="600"
                icon="CA"
                color="#16a34a"
              />
              <SensorGauge
                label="O2 Released"
                :value="currentSensorData.o2Released"
                unit=" ppm"
                :min="0"
                :max="300"
                :optimal-min="150"
                :optimal-max="250"
                icon="O2"
                color="#0891b2"
              />
            </div>
          </div>

          <div class="sensors-sidebar">
            <ConnectionPanel
              :is-connected="isConnected"
              :connection-mode="connectionMode"
              :connection-error="connectionError"
              :device-status="deviceStatus"
              :esp32-ip="esp32Ip"
              @connect="handleConnect"
              @disconnect="disconnect"
              @update-ip="handleUpdateIp"
            />
          </div>
        </div>
      </section>

      <!-- ==================== IDENTIFY PAGE ==================== -->
      <section v-if="currentPage === 'identify'" class="page">
        <div class="identify-layout">
          <div class="identify-main">
            <TreeIdentifier
              @identified="handleTreeIdentified"
              @species-selected="handleSpeciesSelected"
            />
          </div>
          <div class="identify-sidebar">
            <ChaveAnalysisPanel :species="selectedSpecies" :chave-result="chaveResult" />
          </div>
        </div>
      </section>

      <!-- ==================== HISTORY PAGE ==================== -->
      <section v-if="currentPage === 'history'" class="page">
        <div class="card">
          <h2>Identification History</h2>
          <p class="card-description">All trees identified with Chave equation analysis</p>

          <div class="history-table">
            <div class="table-header-row">
              <div class="col-species">Species</div>
              <div class="col-confidence">Confidence</div>
              <div class="col-credits">Credits</div>
              <div class="col-date">Date</div>
            </div>

            <div v-for="item in identificationHistory" :key="item.id" class="table-row">
              <div class="col-species">
                <strong>{{ item.species }}</strong>
              </div>
              <div class="col-confidence">
                <span class="badge">{{ item.confidence }}%</span>
              </div>
              <div class="col-credits">
                <span class="credit-text">{{ item.credits.toFixed(4) }}</span>
              </div>
              <div class="col-date">{{ item.date }}</div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* ============ ROOT ============ */
.saas-app {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  color: #1e293b;
}

/* ============ SIDEBAR ============ */
.sidebar {
  width: 240px;
  background: #0f172a;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  padding: 16px;
  transition: width 0.3s ease;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  overflow-y: auto;
  z-index: 20;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #1e293b;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  color: #16a34a;
  flex-shrink: 0;
}

.logo-text {
  font-size: 1.2rem;
  font-weight: 800;
  color: #f8fafc;
  letter-spacing: -0.5px;
}

.toggle-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.toggle-btn:hover {
  color: #e2e8f0;
  background: #1e293b;
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: transparent;
  border: none;
  color: #94a3b8;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  text-align: left;
}

.nav-item:hover {
  background: #1e293b;
  color: #e2e8f0;
}

.nav-item.active {
  background: #16a34a14;
  color: #16a34a;
  font-weight: 600;
}

.nav-icon {
  flex-shrink: 0;
}

.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-footer {
  padding-top: 16px;
  border-top: 1px solid #1e293b;
}

.connection-mini {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.7rem;
  color: #64748b;
  padding: 8px 12px;
  background: #1e293b;
  border-radius: 8px;
}

.mini-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #64748b;
}

.mini-dot.online {
  background: #16a34a;
  box-shadow: 0 0 6px #16a34a80;
}

/* ============ MAIN CONTENT ============ */
.main-content {
  flex: 1;
  margin-left: 240px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content.sidebar-collapsed {
  margin-left: 64px;
}

/* ============ HEADER ============ */
.top-header {
  background: #ffffff;
  padding: 16px 28px;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content h1 {
  font-size: 1.4rem;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
}

.header-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  background: #dc262614;
  color: #dc2626;
  letter-spacing: 1px;
}

.pulse-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #dc2626;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-mini {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.score-mini-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #94a3b8;
}

.score-mini-value {
  font-size: 1rem;
  font-weight: 800;
  color: #16a34a;
}

/* ============ PAGE ============ */
.page {
  padding: 24px 28px;
  flex: 1;
}

/* ============ METRICS GRID ============ */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

.metric-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.metric-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.metric-header h3 {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-icon {
  flex-shrink: 0;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 800;
  margin-bottom: 6px;
  letter-spacing: -1px;
}

.metric-value.green { color: #16a34a; }
.metric-value.blue { color: #0284c7; }
.metric-value.purple { color: #7c3aed; }
.metric-value.orange { color: #ea580c; }

.metric-change {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}

.metric-change.positive {
  color: #16a34a;
}

.progress-bar {
  width: 100%;
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
  margin: 8px 0 4px;
}

.progress-fill {
  height: 100%;
  background: #7c3aed;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.metric-target {
  font-size: 0.7rem;
  color: #94a3b8;
}

/* ============ DASHBOARD GRID ============ */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

@media (max-width: 1024px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

/* ============ CARD ============ */
.card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.card h2 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.card-description {
  color: #64748b;
  font-size: 0.85rem;
  margin-bottom: 16px;
}

.card-badge {
  font-size: 0.55rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-badge.websocket {
  background: #16a34a14;
  color: #16a34a;
}

.card-badge.polling {
  background: #0284c714;
  color: #0284c7;
}

.card-badge.simulated {
  background: #ea580c14;
  color: #ea580c;
}

/* ============ MINI SENSORS ============ */
.mini-sensors {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.mini-sensor {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.ms-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.ms-value {
  font-size: 1rem;
  font-weight: 700;
  color: #1e293b;
}

.ms-value.warn {
  color: #ea580c;
}

.ms-value.good {
  color: #16a34a;
}

/* ============ RECENT LIST ============ */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 8px;
  transition: all 0.2s;
}

.recent-item:hover {
  background: #f0fdf4;
}

.recent-icon-wrap {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #16a34a14;
  border-radius: 8px;
}

.recent-details {
  flex: 1;
  min-width: 0;
}

.recent-details h4 {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
}

.recent-details p {
  font-size: 0.7rem;
  color: #94a3b8;
}

.badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  background: #16a34a14;
  color: #16a34a;
  white-space: nowrap;
}

/* ============ CALCULATOR LAYOUT ============ */
.calculator-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 20px;
  align-items: start;
}

@media (max-width: 1200px) {
  .calculator-layout {
    grid-template-columns: 1fr;
  }
}

.calc-sensors {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sensor-gauges-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

@media (max-width: 900px) {
  .sensor-gauges-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.calc-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 80px;
}

.card-flat {
  background: #ffffff;
  border-radius: 12px;
  padding: 18px;
  border: 1px solid #e2e8f0;
}

.card-flat h4 {
  font-size: 0.85rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 10px;
}

.species-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.species-option {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 6px 12px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.species-option:hover {
  border-color: #16a34a80;
}

.species-option.active {
  border-color: #16a34a;
  background: #f0fdf4;
  color: #16a34a;
}

/* ============ SENSORS LAYOUT ============ */
.sensors-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  align-items: start;
}

@media (max-width: 1100px) {
  .sensors-layout {
    grid-template-columns: 1fr;
  }
}

.sensors-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sensor-gauges-grid-full {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

@media (max-width: 1100px) {
  .sensor-gauges-grid-full {
    grid-template-columns: repeat(2, 1fr);
  }
}

.sensors-sidebar {
  position: sticky;
  top: 80px;
}

/* ============ IDENTIFY LAYOUT ============ */
.identify-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: start;
}

@media (max-width: 1024px) {
  .identify-layout {
    grid-template-columns: 1fr;
  }
}

/* ============ HISTORY TABLE ============ */
.history-table {
  margin-top: 16px;
}

.table-header-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px 8px 0 0;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  font-size: 0.7rem;
  letter-spacing: 0.5px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  align-items: center;
  font-size: 0.85rem;
  transition: background 0.2s;
}

.table-row:hover {
  background: #f8fafc;
}

.col-species strong {
  color: #1e293b;
  font-weight: 600;
}

.credit-text {
  font-weight: 600;
  color: #16a34a;
}

.col-date {
  color: #94a3b8;
  font-size: 0.8rem;
}

/* ============ BUTTONS ============ */
.btn-secondary {
  padding: 6px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #f8fafc;
  color: #475569;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #f1f5f9;
}

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {
  .sidebar {
    width: 64px;
  }

  .main-content {
    margin-left: 64px;
  }

  .page {
    padding: 16px;
  }

  .mini-sensors {
    grid-template-columns: repeat(2, 1fr);
  }

  .sensor-gauges-grid,
  .sensor-gauges-grid-full {
    grid-template-columns: 1fr;
  }

  .calculator-layout,
  .sensors-layout,
  .identify-layout {
    grid-template-columns: 1fr;
  }

  .table-header-row,
  .table-row {
    grid-template-columns: 1.5fr 1fr;
  }

  .col-credits,
  .col-date {
    display: none;
  }
}
</style>
