<script setup lang="ts">
import { ref, onMounted } from 'vue'

// Sample data - will be replaced with Firebase data later
const temperature = ref(25.4)
const humidity = ref(65)
const soilMoisture = ref(45)
const lightLevel = ref(78)
const carbonCredits = ref(120.5)
const treeSpecies = ref('Mango Tree')
const imageFile = ref<File | null>(null)
const identificationResult = ref('')
const isIdentifying = ref(false)
const errorMessage = ref('')
const imagePreview = ref('')

const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    imageFile.value = target.files[0]
    identificationResult.value = ''
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
    
    // Try to connect to local inference server
    const response = await fetch('http://localhost:5000/identify', {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('Failed to identify tree')
    }
    
    const result = await response.json()
    
    if (result.success) {
      const confidence = (result.confidence * 100).toFixed(1)
      identificationResult.value = `✅ ${result.species} (${confidence}% confidence)`
      treeSpecies.value = result.species
      
      // Update carbon credits based on detection
      carbonCredits.value = result.carbon_rate_kg_per_month * 12
    } else {
      errorMessage.value = result.error || 'Failed to identify tree'
    }
  } catch (error) {
    console.error('Tree identification error:', error)
    errorMessage.value = '⚠️ Backend server not available. Please start the inference server on port 5000.'
    
    // Fallback: Simple mock identification based on filename
    const fileName = file.name.toLowerCase()
    if (fileName.includes('mango')) {
      identificationResult.value = '🥭 Mango Tree (Mock Detection - 95% confidence)'
      treeSpecies.value = 'Mango Tree'
    } else if (fileName.includes('coconut')) {
      identificationResult.value = '🥥 Coconut Tree (Mock Detection - 92% confidence)'
      treeSpecies.value = 'Coconut Tree'
    } else {
      identificationResult.value = '🌳 Unknown Tree Species (Mock Detection)'
    }
  } finally {
    isIdentifying.value = false
  }
}

const refreshData = () => {
  // Simulate data refresh
  temperature.value = (Math.random() * 10 + 20).toFixed(1) as any
  humidity.value = Math.floor(Math.random() * 30 + 50)
  soilMoisture.value = Math.floor(Math.random() * 40 + 30)
  lightLevel.value = Math.floor(Math.random() * 30 + 60)
}
</script>

<template>
  <div class="app">
    <!-- Header -->
    <header class="header">
      <div class="container header-content">
        <div>
          <h1>🌱 HCCMS Dashboard</h1>
          <p>Household Carbon Credit Monitoring System</p>
        </div>
        <div class="status-indicator">
          <div class="status-dot" :class="{ 'status-offline': errorMessage }"></div>
          <span>{{ errorMessage ? 'Backend Offline' : 'System Online' }}</span>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container">
      <!-- Carbon Credits Card -->
      <div class="card credits-card">
        <h2>🏆 Carbon Credits</h2>
        <div class="credits-value">{{ carbonCredits }} kg CO₂</div>
        <p class="credits-info">Total carbon offset this month</p>
      </div>

      <!-- Sensor Data Grid -->
      <div class="grid">
        <div class="card sensor-card">
          <div class="sensor-icon">🌡️</div>
          <h3>Temperature</h3>
          <div class="sensor-value">{{ temperature }}°C</div>
        </div>

        <div class="card sensor-card">
          <div class="sensor-icon">💧</div>
          <h3>Humidity</h3>
          <div class="sensor-value">{{ humidity }}%</div>
        </div>

        <div class="card sensor-card">
          <div class="sensor-icon">🌾</div>
          <h3>Soil Moisture</h3>
          <div class="sensor-value">{{ soilMoisture }}%</div>
        </div>

        <div class="card sensor-card">
          <div class="sensor-icon">☀️</div>
          <h3>Light Level</h3>
          <div class="sensor-value">{{ lightLevel }}%</div>
        </div>
      </div>

      <!-- Tree Identification -->
      <div class="card">
        <h2>🌳 Tree Identification</h2>
        <p class="card-description">Upload an image of tree bark to identify the species using AI</p>
        <div class="identification-section">
          <div class="upload-area">
            <input 
              type="file" 
              id="imageUpload" 
              accept="image/*" 
              @change="handleImageUpload"
              class="file-input"
              :disabled="isIdentifying"
            />
            <label for="imageUpload" class="upload-label" :class="{ disabled: isIdentifying }">
              {{ isIdentifying ? '⏳ Processing...' : '📷 Upload Tree Image' }}
            </label>
          </div>
          
          <!-- Image Preview -->
          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="Uploaded tree image" />
          </div>
          
          <!-- Loading State -->
          <div v-if="isIdentifying" class="loading">
            <div class="spinner"></div>
            <p>Analyzing image...</p>
          </div>
          
          <!-- Error Message -->
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
          
          <!-- Results -->
          <div v-if="identificationResult && !isIdentifying" class="result">
            {{ identificationResult }}
          </div>
          <div v-else-if="!isIdentifying && !imagePreview" class="current-tree">
            Current Species: <strong>{{ treeSpecies }}</strong>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="actions">
        <button @click="refreshData" class="btn btn-primary">🔄 Refresh Data</button>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>HCCMS - Monitoring your environmental impact 🌍</p>
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  width: 100%;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 20px 0;
  margin-bottom: 30px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 2.5rem;
}

.header p {
  margin: 5px 0 0 0;
  color: #7f8c8d;
  font-size: 1rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8f9fa;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #2c3e50;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #4caf50;
  animation: pulse 2s infinite;
}

.status-dot.status-offline {
  background: #ff9800;
  animation: none;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

main {
  flex: 1;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.credits-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
}

.credits-card h2 {
  margin-top: 0;
  font-size: 1.5rem;
}

.credits-value {
  font-size: 3rem;
  font-weight: bold;
  margin: 15px 0;
}

.credits-info {
  opacity: 0.9;
  font-size: 1rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.sensor-card {
  text-align: center;
}

.sensor-icon {
  font-size: 3rem;
  margin-bottom: 10px;
}

.sensor-card h3 {
  margin: 10px 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.card-description {
  color: #7f8c8d;
  margin: 10px 0 20px 0;
  font-size: 0.95rem;
}

.sensor-value {
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
  margin-top: 10px;
}

.identification-section {
  margin-top: 20px;
}

.upload-area {
  margin-bottom: 20px;
}

.file-input {
  display: none;
}

.upload-label {
  display: inline-block;
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
  font-size: 1rem;
}

.upload-label:hover {
  transform: scale(1.05);
}

.upload-label.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.image-preview {
  margin-top: 20px;
  text-align: center;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 20px;
  color: #667eea;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 10px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  padding: 15px;
  background: #fee;
  border-left: 4px solid #e74c3c;
  border-radius: 4px;
  color: #c0392b;
  margin-top: 15px;
  font-size: 0.95rem;
}

.result, .current-tree {
  padding: 15px;
  background: #f0f7ff;
  border-radius: 8px;
  margin-top: 15px;
  font-size: 1.1rem;
}

.result {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
  color: #2e7d32;
  font-weight: bold;
}

.actions {
  text-align: center;
  margin: 30px 0;
}

.btn {
  padding: 12px 30px;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn:hover {
  transform: scale(1.05);
}

.footer {
  background: rgba(255, 255, 255, 0.95);
  text-align: center;
  padding: 20px;
  margin-top: 40px;
  color: #7f8c8d;
}

.footer p {
  margin: 0;
}
</style>
