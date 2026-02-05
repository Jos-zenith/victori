<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TreeSpecies, ChaveResult, TreeIdentificationResult } from '../types'
import { TREE_SPECIES_DB, calculateChaveResult } from '../utils/carbon-calculations'

const emit = defineEmits<{
  identified: [result: TreeIdentificationResult]
  speciesSelected: [species: TreeSpecies, chave: ChaveResult]
}>()

const imageFile = ref<File | null>(null)
const imagePreview = ref('')
const isIdentifying = ref(false)
const errorMessage = ref('')
const identificationResult = ref<TreeIdentificationResult | null>(null)

// Manual species selector for when camera/inference is unavailable
const manualMode = ref(false)
const selectedSpeciesKey = ref('')

const speciesList = computed(() => {
  return Object.entries(TREE_SPECIES_DB).map(([key, species]) => ({
    key,
    ...species,
  }))
})

// ESP32-CAM capture endpoint
const esp32CamUrl = ref('http://192.168.1.100/capture')
const captureFromESP32 = ref(false)

async function handleImageUpload(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    imageFile.value = target.files[0]
    identificationResult.value = null
    errorMessage.value = ''

    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(imageFile.value)

    await identifyTree(imageFile.value)
  }
}

async function captureFromCamera() {
  isIdentifying.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(esp32CamUrl.value, {
      signal: AbortSignal.timeout(10000),
    })
    if (!response.ok) throw new Error('Camera capture failed')
    const blob = await response.blob()
    const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' })

    imageFile.value = file
    imagePreview.value = URL.createObjectURL(blob)

    await identifyTree(file)
  } catch {
    errorMessage.value = 'ESP32-CAM not reachable. Use manual upload or select species manually.'
    isIdentifying.value = false
  }
}

async function identifyTree(file: File) {
  isIdentifying.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('image', file)

    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) throw new Error('Inference failed')

    const result = await response.json()
    const confidence = Math.round(result.confidence * 100)
    const speciesName = result.species as string

    // Find species in our DB
    const speciesKey = Object.keys(TREE_SPECIES_DB).find(
      (k) => TREE_SPECIES_DB[k].name.toLowerCase() === speciesName.toLowerCase()
        || TREE_SPECIES_DB[k].name.toLowerCase().includes(speciesName.toLowerCase().replace(' tree', ''))
    )

    const species = speciesKey ? TREE_SPECIES_DB[speciesKey] : {
      name: speciesName,
      scientificName: 'Unknown',
      woodDensity: 0.50,
      carbonFraction: 0.47,
      avgDbh: 35,
      avgHeight: 20,
      growthRate: 'Medium',
      co2AbsorptionRate: 25.0,
      barkPattern: 'Unknown',
    }

    const chaveResult = calculateChaveResult(species)

    const idResult: TreeIdentificationResult = {
      species: species.name,
      scientificName: species.scientificName,
      confidence,
      confidenceLevel: confidence >= 90 ? 'Very High' : confidence >= 70 ? 'High' : confidence >= 50 ? 'Medium' : 'Low',
      chaveResult,
      carbonRate: chaveResult.co2Sequestered / 12,
      imagePreview: imagePreview.value,
      identifiedAt: new Date().toISOString(),
    }

    identificationResult.value = idResult
    emit('identified', idResult)
    emit('speciesSelected', species, chaveResult)
  } catch {
    errorMessage.value = 'Inference server unavailable. Select species manually below.'
    manualMode.value = true
  } finally {
    isIdentifying.value = false
  }
}

function selectManualSpecies() {
  if (!selectedSpeciesKey.value) return
  const species = TREE_SPECIES_DB[selectedSpeciesKey.value]
  if (!species) return

  const chaveResult = calculateChaveResult(species)

  const idResult: TreeIdentificationResult = {
    species: species.name,
    scientificName: species.scientificName,
    confidence: 100,
    confidenceLevel: 'Manual Selection',
    chaveResult,
    carbonRate: chaveResult.co2Sequestered / 12,
    imagePreview: imagePreview.value,
    identifiedAt: new Date().toISOString(),
  }

  identificationResult.value = idResult
  emit('identified', idResult)
  emit('speciesSelected', species, chaveResult)
}

function clearAll() {
  imageFile.value = null
  imagePreview.value = ''
  identificationResult.value = null
  errorMessage.value = ''
  selectedSpeciesKey.value = ''
}
</script>

<template>
  <div class="tree-identifier">
    <div class="id-header">
      <h3>Tree Bark Identification</h3>
      <div class="id-modes">
        <button class="mode-btn" :class="{ active: !captureFromESP32 }" @click="captureFromESP32 = false">Upload</button>
        <button class="mode-btn" :class="{ active: captureFromESP32 }" @click="captureFromESP32 = true">ESP32-CAM</button>
      </div>
    </div>

    <!-- Upload Mode -->
    <div v-if="!captureFromESP32" class="upload-area">
      <input
        type="file"
        id="treeImageUpload"
        accept="image/*"
        @change="handleImageUpload"
        class="file-input"
        :disabled="isIdentifying"
      />
      <label for="treeImageUpload" class="upload-label">
        <div class="upload-icon-large">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17,8 12,3 7,8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </div>
        <span class="upload-text">Upload tree bark image</span>
        <span class="upload-hint">PNG, JPG up to 10MB</span>
      </label>
    </div>

    <!-- ESP32-CAM Mode -->
    <div v-else class="cam-area">
      <div class="cam-config">
        <label>Camera URL</label>
        <input v-model="esp32CamUrl" type="text" class="cam-input" placeholder="http://192.168.1.100/capture" />
      </div>
      <button class="capture-btn" :disabled="isIdentifying" @click="captureFromCamera">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
          <circle cx="12" cy="13" r="4"/>
        </svg>
        {{ isIdentifying ? 'Capturing...' : 'Capture from ESP32-CAM' }}
      </button>
    </div>

    <!-- Image Preview -->
    <div v-if="imagePreview" class="preview-container">
      <img :src="imagePreview" alt="Tree bark image" class="preview-image" />
      <button class="clear-btn" @click="clearAll">Clear</button>
    </div>

    <!-- Loading -->
    <div v-if="isIdentifying" class="id-loading">
      <div class="id-spinner"></div>
      <p>Analyzing bark pattern with AI...</p>
    </div>

    <!-- Error -->
    <div v-if="errorMessage" class="id-error">
      {{ errorMessage }}
    </div>

    <!-- Manual Species Selection -->
    <div v-if="manualMode || (!identificationResult && !isIdentifying)" class="manual-section">
      <div class="manual-header">
        <span class="manual-label">Or select species manually</span>
      </div>
      <div class="species-grid">
        <button
          v-for="s in speciesList"
          :key="s.key"
          class="species-btn"
          :class="{ selected: selectedSpeciesKey === s.key }"
          @click="selectedSpeciesKey = s.key"
        >
          <strong>{{ s.name }}</strong>
          <em>{{ s.scientificName }}</em>
        </button>
      </div>
      <button
        v-if="selectedSpeciesKey"
        class="analyze-btn"
        @click="selectManualSpecies"
      >
        Run Chave Analysis
      </button>
    </div>

    <!-- Identification Result -->
    <div v-if="identificationResult && !isIdentifying" class="id-result">
      <div class="result-badge">
        <h4>{{ identificationResult.species }}</h4>
        <em>{{ identificationResult.scientificName }}</em>
        <div class="confidence-row">
          <span class="conf-value">{{ identificationResult.confidence }}%</span>
          <span class="conf-level">{{ identificationResult.confidenceLevel }}</span>
        </div>
      </div>

      <div class="result-stats">
        <div class="stat-item">
          <span class="stat-label">Biomass (AGB)</span>
          <span class="stat-value">{{ identificationResult.chaveResult.agb.toLocaleString() }} kg</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">CO2 Sequestered</span>
          <span class="stat-value">{{ identificationResult.chaveResult.co2Sequestered.toLocaleString() }} kg</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Carbon Credits</span>
          <span class="stat-value credits">{{ identificationResult.chaveResult.carbonCredits.toFixed(4) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Value (USD)</span>
          <span class="stat-value usd">${{ identificationResult.chaveResult.creditValueUSD.toFixed(2) }}</span>
        </div>
      </div>

      <button class="new-scan-btn" @click="clearAll">New Scan</button>
    </div>
  </div>
</template>

<style scoped>
.tree-identifier {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #e8eef7;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.id-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.id-header h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1e293b;
}

.id-modes {
  display: flex;
  gap: 4px;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 3px;
}

.mode-btn {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 5px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background: transparent;
  color: #64748b;
  transition: all 0.2s;
}

.mode-btn.active {
  background: #ffffff;
  color: #1e293b;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.file-input {
  display: none;
}

.upload-area {
  margin-bottom: 14px;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 30px 20px;
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f8fafc;
}

.upload-label:hover {
  border-color: #0284c7;
  background: #f0f9ff;
}

.upload-text {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}

.upload-hint {
  font-size: 0.7rem;
  color: #94a3b8;
}

.cam-area {
  margin-bottom: 14px;
}

.cam-config {
  margin-bottom: 10px;
}

.cam-config label {
  display: block;
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 4px;
}

.cam-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.8rem;
  color: #1e293b;
  outline: none;
}

.cam-input:focus {
  border-color: #0284c7;
}

.capture-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: #1e293b;
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.capture-btn:hover:not(:disabled) {
  background: #334155;
}

.capture-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.preview-container {
  position: relative;
  margin-bottom: 14px;
}

.preview-image {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 10px;
}

.clear-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px 10px;
  border: none;
  border-radius: 6px;
  background: rgba(0,0,0,0.6);
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
}

.id-loading {
  text-align: center;
  padding: 24px;
}

.id-spinner {
  width: 36px;
  height: 36px;
  margin: 0 auto 10px;
  border: 3px solid #e2e8f0;
  border-top-color: #16a34a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.id-loading p {
  font-size: 0.8rem;
  color: #64748b;
}

.id-error {
  font-size: 0.75rem;
  color: #dc2626;
  background: #fef2f2;
  padding: 10px 14px;
  border-radius: 8px;
  margin-bottom: 14px;
  border-left: 3px solid #dc2626;
}

.manual-section {
  margin-top: 10px;
}

.manual-header {
  margin-bottom: 10px;
}

.manual-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

.species-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
  margin-bottom: 12px;
}

.species-btn {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.species-btn:hover {
  border-color: #16a34a80;
  background: #f0fdf4;
}

.species-btn.selected {
  border-color: #16a34a;
  background: #f0fdf4;
}

.species-btn strong {
  font-size: 0.75rem;
  color: #1e293b;
}

.species-btn em {
  font-size: 0.6rem;
  color: #94a3b8;
}

.analyze-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: #16a34a;
  color: white;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.analyze-btn:hover {
  background: #15803d;
}

.id-result {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-badge {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, #16a34a 0%, #0f766e 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 14px;
}

.result-badge h4 {
  font-size: 1.3rem;
  margin-bottom: 2px;
}

.result-badge em {
  font-size: 0.8rem;
  opacity: 0.85;
}

.confidence-row {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.conf-value {
  font-size: 1.2rem;
  font-weight: 800;
}

.conf-level {
  font-size: 0.7rem;
  padding: 2px 8px;
  background: rgba(255,255,255,0.2);
  border-radius: 10px;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 14px;
}

.stat-item {
  padding: 10px;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.6rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1e293b;
}

.stat-value.credits {
  color: #16a34a;
}

.stat-value.usd {
  color: #0284c7;
}

.new-scan-btn {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
  color: #475569;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.new-scan-btn:hover {
  background: #f1f5f9;
}
</style>
