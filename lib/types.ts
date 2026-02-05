export interface SensorData {
  temperature: number
  humidity: number
  soilMoisture: number
  lightIntensity: number
  ph: number
  co2Emitted: number
  co2Absorbed: number
  o2Released: number
  timestamp: string
}

export interface TreeSpecies {
  name: string
  scientificName: string
  woodDensity: number // g/cm^3
  carbonFraction: number
  avgDbh: number // cm - Diameter at Breast Height
  avgHeight: number // meters
  growthRate: string
  co2AbsorptionRate: number // kg CO2/year
}

export interface ChaveResult {
  agb: number // Above Ground Biomass (kg)
  carbonStored: number // kg of carbon
  co2Sequestered: number // kg CO2 equivalent
  carbonCredits: number
  creditValueUSD: number
}

export interface CarbonCreditScore {
  totalScore: number
  grade: string
  breakdown: {
    sequestrationScore: number
    emissionOffset: number
    environmentalHealth: number
    oxygenProduction: number
  }
  creditsEarned: number
  creditValueUSD: number
  netCarbonBalance: number
}

export interface DeviceStatus {
  id: string
  name: string
  status: "online" | "offline" | "error"
  lastHeartbeat: string
  batteryLevel: number
  firmwareVersion: string
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
