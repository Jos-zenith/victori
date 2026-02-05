<script setup lang="ts">
import { ref } from 'vue'

// UI State
const sidebarOpen = ref(true)
const currentPage = ref('dashboard')
const imageFile = ref<File | null>(null)
const imagePreview = ref('')
const isIdentifying = ref(false)
const errorMessage = ref('')
const selectedSpecies = ref<{name: string, confidence: number, co2_monthly: number} | null>(null)

// Dashboard metrics
const totalTrees = ref(5)
const totalCO2Offset = ref(2450.8)
const monthlyTarget = ref(500)
const currentMonth = ref(245.5)
const lastIdentifications = ref<Array<{id: number, species: string, confidence: number, date: string}>>([
  { id: 1, species: 'Mango Tree', confidence: 94, date: '2 hours ago' },
  { id: 2, species: 'Coconut Tree', confidence: 89, date: '5 hours ago' },
  { id: 3, species: 'Mango Tree', confidence: 91, date: '1 day ago' }
])

const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    imageFile.value = target.files[0]
    selectedSpecies.value = null
    errorMessage.value = ''
    
    // Create image preview
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(imageFile.value)
    
    // Send to backend API
    await identifyTree(imageFile.value)
  }
}

const identifyTree = async (file: File) => {
  isIdentifying.value = true
  errorMessage.value = ''
  
  try {
    const formData = new FormData()
    formData.append('image', file)
    
    // Connect to inference server
    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('Failed to identify tree')
    }
    
    const result = await response.json()
    const confidence = Math.round(result.confidence * 100)
    
    // Calculate CO2 based on species and DBH (assuming default)
    const co2Monthly = calculateCO2(result.species)
    
    selectedSpecies.value = {
      name: result.species,
      confidence: confidence,
      co2_monthly: co2Monthly
    }
    
    // Add to history
    lastIdentifications.value.unshift({
      id: lastIdentifications.value.length + 1,
      species: result.species,
      confidence: confidence,
      date: 'Just now'
    })
  } catch (error) {
    console.error('Tree identification error:', error)
    errorMessage.value = 'Backend server not available. Please ensure the inference server is running on port 5000.'
  } finally {
    isIdentifying.value = false
  }
}

const calculateCO2 = (species: string): number => {
  // CO2 sequestration rates (kg/month) - can be expanded with species data
  const rates: {[key: string]: number} = {
    'Mango Tree': 4.2,
    'Coconut Tree': 3.8,
    'default': 4.0
  }
  return rates[species] ?? rates['default']!
}

const clearImage = () => {
  imageFile.value = null
  imagePreview.value = ''
  selectedSpecies.value = null
}
</script>

<template>
  <div class="saas-app">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: !sidebarOpen }">
      <div class="sidebar-header">
        <div class="logo">🌱 Victori</div>
        <button class="toggle-btn" @click="sidebarOpen = !sidebarOpen">☰</button>
      </div>
      
      <nav class="sidebar-nav">
        <button 
          @click="currentPage = 'dashboard'"
          class="nav-item" 
          :class="{ active: currentPage === 'dashboard' }"
        >
          <span class="icon">📊</span>
          <span class="label">Dashboard</span>
        </button>
        <button 
          @click="currentPage = 'identify'"
          class="nav-item" 
          :class="{ active: currentPage === 'identify' }"
        >
          <span class="icon">🔍</span>
          <span class="label">Identify Trees</span>
        </button>
        <button 
          @click="currentPage = 'history'"
          class="nav-item" 
          :class="{ active: currentPage === 'history' }"
        >
          <span class="icon">📜</span>
          <span class="label">History</span>
        </button>
      </nav>
      
      <div class="sidebar-footer">
        <button class="nav-item">
          <span class="icon">⚙️</span>
          <span class="label">Settings</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="top-header">
        <div class="header-content">
          <h1>{{ currentPage === 'dashboard' ? 'Dashboard' : currentPage === 'identify' ? 'Tree Identification' : 'History' }}</h1>
          <div class="user-profile">
            <span class="user-name">Welcome back! 👋</span>
            <div class="avatar">👤</div>
          </div>
        </div>
      </header>

      <!-- Dashboard Page -->
      <section v-if="currentPage === 'dashboard'" class="page">
        <!-- Key Metrics Row -->
        <div class="metrics-grid">
          <div class="metric-card">
            <div class="metric-header">
              <h3>Total Trees</h3>
              <span class="icon">🌳</span>
            </div>
            <div class="metric-value">{{ totalTrees }}</div>
            <p class="metric-change">+1 this month</p>
          </div>
          
          <div class="metric-card">
            <div class="metric-header">
              <h3>Total CO₂ Offset</h3>
              <span class="icon">🌍</span>
            </div>
            <div class="metric-value">{{ totalCO2Offset }} kg</div>
            <p class="metric-change">↑ 12% from last month</p>
          </div>
          
          <div class="metric-card">
            <div class="metric-header">
              <h3>This Month</h3>
              <span class="icon">📈</span>
            </div>
            <div class="metric-value">{{ currentMonth }} kg</div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: (currentMonth / monthlyTarget * 100) + '%' }"></div>
            </div>
            <p class="metric-target">Target: {{ monthlyTarget }} kg</p>
          </div>
          
          <div class="metric-card">
            <div class="metric-header">
              <h3>Credits Earned</h3>
              <span class="icon">🏆</span>
            </div>
            <div class="metric-value">{{ Math.round(totalCO2Offset / 10) }}</div>
            <p class="metric-change">+5 credits this month</p>
          </div>
        </div>

        <!-- Recent Identifications -->
        <div class="card">
          <div class="card-header">
            <h2>Recent Identifications</h2>
            <button class="btn-secondary">View All</button>
          </div>
          
          <div class="recent-list">
            <div v-for="item in lastIdentifications" :key="item.id" class="recent-item">
              <div class="recent-icon">🌳</div>
              <div class="recent-details">
                <h4>{{ item.species }}</h4>
                <p>{{ item.date }} • {{ item.confidence }}% confidence</p>
              </div>
              <span class="badge">{{ item.confidence }}%</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Identify Page -->
      <section v-if="currentPage === 'identify'" class="page">
        <div class="identify-container">
          <div class="upload-section">
            <div class="card">
              <h2>Upload Tree Image</h2>
              <p class="card-description">Upload a clear image of tree bark for AI-powered identification</p>
              
              <div class="upload-drop-area">
                <input 
                  type="file" 
                  id="imageUpload" 
                  accept="image/*" 
                  @change="handleImageUpload"
                  class="file-input"
                  :disabled="isIdentifying"
                />
                <label for="imageUpload" class="upload-drop-label">
                  <div class="upload-icon">📸</div>
                  <h3>Click to upload or drag and drop</h3>
                  <p>PNG, JPG, GIF up to 10MB</p>
                </label>
              </div>

              <!-- Error Message -->
              <div v-if="errorMessage" class="alert alert-error">
                <span class="alert-icon">⚠️</span>
                {{ errorMessage }}
              </div>
            </div>
          </div>

          <!-- Results Section -->
          <div v-if="imagePreview || selectedSpecies" class="results-section">
            <div class="card">
              <div class="card-header">
                <h2>Identification Result</h2>
                <button @click="clearImage" class="btn-link">Clear</button>
              </div>

              <!-- Image Preview -->
              <div v-if="imagePreview" class="result-image-container">
                <img :src="imagePreview" alt="Uploaded tree image" class="result-image" />
              </div>

              <!-- Loading State -->
              <div v-if="isIdentifying" class="loading-state">
                <div class="spinner"></div>
                <p>Analyzing image with AI...</p>
              </div>

              <!-- Results -->
              <div v-if="selectedSpecies && !isIdentifying" class="result-content">
                <div class="species-badge">
                  <h3>{{ selectedSpecies.name }}</h3>
                  <span class="confidence">{{ selectedSpecies.confidence }}% confident</span>
                </div>

                <div class="result-details">
                  <div class="detail-item">
                    <span class="detail-label">Species</span>
                    <span class="detail-value">{{ selectedSpecies.name }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Confidence</span>
                    <span class="detail-value">{{ selectedSpecies.confidence }}%</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">CO₂ Monthly Sequestration</span>
                    <span class="detail-value">{{ selectedSpecies.co2_monthly }} kg</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Annual Offset</span>
                    <span class="detail-value">{{ (selectedSpecies.co2_monthly * 12).toFixed(1) }} kg</span>
                  </div>
                </div>

                <button class="btn-primary" @click="clearImage">Identify Another Tree</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- History Page -->
      <section v-if="currentPage === 'history'" class="page">
        <div class="card">
          <h2>Identification History</h2>
          <p class="card-description">All trees you've identified</p>
          
          <div class="history-table">
            <div class="table-header">
              <div class="col-species">Species</div>
              <div class="col-confidence">Confidence</div>
              <div class="col-date">Date</div>
              <div class="col-action">Action</div>
            </div>
            
            <div v-for="item in lastIdentifications" :key="item.id" class="table-row">
              <div class="col-species">{{ item.species }}</div>
              <div class="col-confidence">
                <span class="badge">{{ item.confidence }}%</span>
              </div>
              <div class="col-date">{{ item.date }}</div>
              <div class="col-action">
                <button class="btn-text">View</button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.saas-app {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  color: #2c3e50;
}

/* ============ SIDEBAR ============ */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  padding: 20px;
  transition: width 0.3s ease;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  overflow-y: auto;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  white-space: nowrap;
}

.sidebar.collapsed .logo {
  font-size: 1.8rem;
}

.toggle-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  display: none;
}

@media (max-width: 768px) {
  .toggle-btn {
    display: block;
  }
}

.sidebar-nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.95rem;
  white-space: nowrap;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(4px);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.3);
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.icon {
  font-size: 1.3rem;
  min-width: 30px;
}

.label {
  flex: 1;
}

.sidebar.collapsed .label {
  display: none;
}

.sidebar-footer {
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

/* ============ MAIN CONTENT ============ */
.main-content {
  flex: 1;
  margin-left: 260px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 80px;
  }
}

/* ============ TOP HEADER ============ */
.top-header {
  background: white;
  padding: 20px 30px;
  border-bottom: 1px solid #e8eef7;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.header-content h1 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-size: 0.95rem;
  color: #7f8c8d;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  cursor: pointer;
}

/* ============ PAGE CONTENT ============ */
.page {
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* ============ METRICS GRID ============ */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #f0f4f8;
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.metric-header h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-header .icon {
  font-size: 1.8rem;
}

.metric-value {
  font-size: 2.2rem;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 10px;
}

.metric-change {
  font-size: 0.85rem;
  color: #95a5a6;
  margin: 0;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #ecf0f1;
  border-radius: 3px;
  overflow: hidden;
  margin: 10px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.metric-target {
  font-size: 0.85rem;
  color: #95a5a6;
  margin-top: 8px;
}

/* ============ CARDS ============ */
.card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f4f8;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f4f8;
}

.card h2 {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.card-description {
  color: #7f8c8d;
  margin-bottom: 20px;
  font-size: 0.95rem;
}

/* ============ UPLOAD SECTION ============ */
.identify-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

@media (max-width: 1024px) {
  .identify-container {
    grid-template-columns: 1fr;
  }
}

.upload-drop-area {
  position: relative;
}

.file-input {
  display: none;
}

.upload-drop-label {
  display: block;
  padding: 40px 20px;
  border: 2px dashed #bdc3c7;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.upload-drop-label:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 10px;
  display: block;
}

.upload-drop-label h3 {
  color: #2c3e50;
  margin-bottom: 5px;
}

.upload-drop-label p {
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* ============ RESULTS SECTION ============ */
.result-image-container {
  text-align: center;
  margin-bottom: 25px;
}

.result-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.loading-state {
  text-align: center;
  padding: 40px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 15px;
  border: 4px solid #ecf0f1;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.result-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.species-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  text-align: center;
}

.species-badge h3 {
  font-size: 1.8rem;
  margin-bottom: 5px;
}

.confidence {
  font-size: 0.95rem;
  opacity: 0.9;
}

.result-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 25px;
}

.detail-item {
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.detail-label {
  display: block;
  font-size: 0.85rem;
  color: #7f8c8d;
  text-transform: uppercase;
  margin-bottom: 5px;
}

.detail-value {
  display: block;
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
}

/* ============ RECENT LIST ============ */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.recent-item:hover {
  background: #f0f4ff;
  transform: translateX(4px);
}

.recent-icon {
  font-size: 2rem;
  min-width: 40px;
}

.recent-details {
  flex: 1;
}

.recent-details h4 {
  font-size: 1rem;
  color: #2c3e50;
  margin-bottom: 3px;
}

.recent-details p {
  font-size: 0.85rem;
  color: #95a5a6;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

/* ============ HISTORY TABLE ============ */
.history-table {
  margin-top: 20px;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr 1fr;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
  font-weight: 700;
  color: #7f8c8d;
  text-transform: uppercase;
  font-size: 0.85rem;
  border-bottom: 2px solid #ecf0f1;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr 1fr;
  gap: 15px;
  padding: 15px;
  border-bottom: 1px solid #f0f4f8;
  align-items: center;
  transition: background 0.3s ease;
}

.table-row:hover {
  background: #f8f9fa;
}

.col-species {
  color: #2c3e50;
  font-weight: 600;
}

/* ============ ALERTS ============ */
.alert {
  padding: 15px;
  border-radius: 8px;
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.95rem;
}

.alert-error {
  background: #fee;
  color: #c0392b;
  border-left: 4px solid #e74c3c;
}

.alert-icon {
  font-size: 1.2rem;
}

/* ============ BUTTONS ============ */
.btn-primary, .btn-secondary, .btn-link, .btn-text {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  font-weight: 600;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 100%;
  padding: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f0f4f8;
  color: #667eea;
  border: 1px solid #e8eef7;
}

.btn-secondary:hover {
  background: #e8eef7;
}

.btn-link {
  background: none;
  color: #667eea;
  padding: 0;
}

.btn-link:hover {
  opacity: 0.8;
}

.btn-text {
  background: none;
  color: #667eea;
  padding: 0;
  text-decoration: underline;
}

/* ============ RESPONSIVE ============ */
@media (max-width: 768px) {
  .sidebar {
    width: 80px;
  }

  .sidebar.collapsed {
    width: 80px;
  }

  .logo {
    font-size: 1.3rem;
  }

  .main-content {
    margin-left: 60px;
  }

  .page {
    padding: 20px;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .identify-container {
    grid-template-columns: 1fr;
  }

  .table-header, .table-row {
    grid-template-columns: 1.5fr 1fr;
  }

  .col-date, .col-action {
    display: none;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>
