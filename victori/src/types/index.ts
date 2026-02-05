// ==================== SENSOR DATA ====================

export interface SensorData {
  temperature: number       // DHT11 - Celsius
  humidity: number          // DHT11 - Percentage
  soilMoisture: number      // Soil Moisture Sensor - Percentage
  lightIntensity: number    // LDR - micromol/m^2/s
  ph: number                // pH Sensor
  co2Emitted: number        // MQ135 - Vehicle CO2 (ppm)
  co2Absorbed: number       // Calculated - Tree CO2 absorption (ppm)
  o2Released: number        // Calculated - O2 release (ppm)
  timestamp: string
}

export interface SensorHistoryPoint {
  time: string
  temperature: number
  humidity: number
  co2Emitted: number
  co2Absorbed: number
  o2Released: number
  soilMoisture: number
  lightIntensity: number
}

// ==================== TREE SPECIES & CHAVE ====================

export interface TreeSpecies {
  name: string
  scientificName: string
  woodDensity: number       // g/cm^3 (rho)
  carbonFraction: number    // typically 0.47
  avgDbh: number            // cm - Diameter at Breast Height
  avgHeight: number         // meters
  growthRate: string
  co2AbsorptionRate: number // kg CO2/year
  barkPattern: string       // description for identification
}

export interface ChaveResult {
  agb: number               // Above Ground Biomass (kg)
  carbonStored: number      // kg of carbon
  co2Sequestered: number    // kg CO2 equivalent
  carbonCredits: number     // metric tons CO2
  creditValueUSD: number    // market value
}

// ==================== CARBON CREDIT SCORE ====================

export interface CarbonCreditScore {
  totalScore: number        // 0-100
  grade: string             // A+, A, B+, B, C, D, F
  breakdown: {
    sequestrationScore: number
    emissionOffset: number
    environmentalHealth: number
    oxygenProduction: number
  }
  creditsEarned: number
  creditValueUSD: number
  netCarbonBalance: number  // ppm (absorbed - emitted)
}

// ==================== DEVICE STATUS ====================

export interface DeviceStatus {
  id: string
  name: string
  status: 'online' | 'offline' | 'error'
  lastHeartbeat: string
  batteryLevel: number
  firmwareVersion: string
  sensors: string[]
}

export interface ESP32CamCapture {
  imageData: string         // base64
  timestamp: string
  deviceId: string
}

// ==================== TREE IDENTIFICATION ====================

export interface TreeIdentificationResult {
  species: string
  scientificName: string
  confidence: number
  confidenceLevel: string
  chaveResult: ChaveResult
  carbonRate: number        // kg CO2/month
  imagePreview: string
  identifiedAt: string
}

// ==================== WEBSOCKET MESSAGES ====================

export interface SensorMessage {
  type: 'sensor_data' | 'heartbeat' | 'camera_capture' | 'error'
  deviceId: string
  payload: SensorData | ESP32CamCapture | { message: string }
  timestamp: string
}
