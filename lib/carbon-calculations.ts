import type { SensorData, TreeSpecies, ChaveResult, CarbonCreditScore } from "./types"

// Tree species database with Chave equation parameters
export const TREE_SPECIES_DB: Record<string, TreeSpecies> = {
  teak: {
    name: "Teak",
    scientificName: "Tectona grandis",
    woodDensity: 0.55,
    carbonFraction: 0.47,
    avgDbh: 35,
    avgHeight: 25,
    growthRate: "Medium",
    co2AbsorptionRate: 22.6,
  },
  neem: {
    name: "Neem",
    scientificName: "Azadirachta indica",
    woodDensity: 0.65,
    carbonFraction: 0.47,
    avgDbh: 40,
    avgHeight: 20,
    growthRate: "Fast",
    co2AbsorptionRate: 48.0,
  },
  banyan: {
    name: "Banyan",
    scientificName: "Ficus benghalensis",
    woodDensity: 0.45,
    carbonFraction: 0.47,
    avgDbh: 80,
    avgHeight: 25,
    growthRate: "Slow",
    co2AbsorptionRate: 21.8,
  },
  mango: {
    name: "Mango",
    scientificName: "Mangifera indica",
    woodDensity: 0.52,
    carbonFraction: 0.47,
    avgDbh: 45,
    avgHeight: 18,
    growthRate: "Medium",
    co2AbsorptionRate: 35.0,
  },
  peepal: {
    name: "Peepal",
    scientificName: "Ficus religiosa",
    woodDensity: 0.46,
    carbonFraction: 0.47,
    avgDbh: 60,
    avgHeight: 20,
    growthRate: "Fast",
    co2AbsorptionRate: 38.0,
  },
  eucalyptus: {
    name: "Eucalyptus",
    scientificName: "Eucalyptus globulus",
    woodDensity: 0.56,
    carbonFraction: 0.47,
    avgDbh: 30,
    avgHeight: 30,
    growthRate: "Very Fast",
    co2AbsorptionRate: 25.0,
  },
  oak: {
    name: "Oak",
    scientificName: "Quercus robur",
    woodDensity: 0.60,
    carbonFraction: 0.50,
    avgDbh: 50,
    avgHeight: 25,
    growthRate: "Slow",
    co2AbsorptionRate: 21.0,
  },
  pine: {
    name: "Pine",
    scientificName: "Pinus sylvestris",
    woodDensity: 0.42,
    carbonFraction: 0.50,
    avgDbh: 35,
    avgHeight: 25,
    growthRate: "Medium",
    co2AbsorptionRate: 10.0,
  },
}

/**
 * Chave et al. (2014) Improved Pantropical Allometric Model
 * AGB = 0.0673 * (p * D^2 * H)^0.976
 * where:
 *   AGB = Above Ground Biomass (kg)
 *   p = wood density (g/cm^3)
 *   D = DBH (cm)
 *   H = height (m)
 */
export function calculateChaveBiomass(
  woodDensity: number,
  dbh: number,
  height: number
): number {
  const agb = 0.0673 * Math.pow(woodDensity * dbh * dbh * height, 0.976)
  return agb
}

/**
 * Calculate carbon stored from biomass
 * Carbon stored = AGB * carbon fraction
 * CO2 sequestered = carbon stored * (44/12) [molecular weight ratio]
 */
export function calculateChaveResult(species: TreeSpecies): ChaveResult {
  const agb = calculateChaveBiomass(
    species.woodDensity,
    species.avgDbh,
    species.avgHeight
  )
  const carbonStored = agb * species.carbonFraction
  const co2Sequestered = carbonStored * (44 / 12)
  // 1 carbon credit = 1 metric ton CO2
  const carbonCredits = co2Sequestered / 1000
  // Market price ~$30-50 per credit (using $40 average)
  const creditValueUSD = carbonCredits * 40

  return {
    agb: Math.round(agb * 100) / 100,
    carbonStored: Math.round(carbonStored * 100) / 100,
    co2Sequestered: Math.round(co2Sequestered * 100) / 100,
    carbonCredits: Math.round(carbonCredits * 10000) / 10000,
    creditValueUSD: Math.round(creditValueUSD * 100) / 100,
  }
}

/**
 * Environmental factor multiplier based on sensor conditions
 * Better conditions (optimal temp, humidity, sunlight) = higher carbon absorption
 */
function getEnvironmentalMultiplier(sensor: SensorData): number {
  let multiplier = 1.0

  // Temperature factor (optimal: 20-30 C)
  if (sensor.temperature >= 20 && sensor.temperature <= 30) {
    multiplier *= 1.2
  } else if (sensor.temperature >= 15 && sensor.temperature <= 35) {
    multiplier *= 1.0
  } else {
    multiplier *= 0.7
  }

  // Humidity factor (optimal: 40-80%)
  if (sensor.humidity >= 40 && sensor.humidity <= 80) {
    multiplier *= 1.15
  } else if (sensor.humidity >= 20 && sensor.humidity <= 90) {
    multiplier *= 1.0
  } else {
    multiplier *= 0.75
  }

  // Sunlight factor (optimal: 400-800 micromol)
  if (sensor.lightIntensity >= 400 && sensor.lightIntensity <= 800) {
    multiplier *= 1.25
  } else if (sensor.lightIntensity >= 200 && sensor.lightIntensity <= 1000) {
    multiplier *= 1.0
  } else {
    multiplier *= 0.6
  }

  // Soil moisture factor (optimal: 30-70%)
  if (sensor.soilMoisture >= 30 && sensor.soilMoisture <= 70) {
    multiplier *= 1.1
  } else {
    multiplier *= 0.85
  }

  // pH factor (optimal: 5.5-7.5)
  if (sensor.ph >= 5.5 && sensor.ph <= 7.5) {
    multiplier *= 1.1
  } else {
    multiplier *= 0.9
  }

  return multiplier
}

/**
 * Calculate Carbon Credit Score
 * Combines Chave equation biomass with real-time sensor environmental conditions
 */
export function calculateCarbonCreditScore(
  sensor: SensorData,
  species: TreeSpecies
): CarbonCreditScore {
  const chaveResult = calculateChaveResult(species)
  const envMultiplier = getEnvironmentalMultiplier(sensor)

  // Sequestration score (0-100)
  const baseSequestration = Math.min(
    (chaveResult.co2Sequestered / 500) * 100,
    100
  )
  const sequestrationScore = Math.round(baseSequestration * envMultiplier)

  // Emission offset score - how well trees offset car CO2
  const emissionOffset = Math.round(
    Math.min((sensor.co2Absorbed / Math.max(sensor.co2Emitted, 1)) * 100, 100)
  )

  // Environmental health (based on sensor readings quality)
  const tempScore =
    sensor.temperature >= 18 && sensor.temperature <= 32 ? 100 : 50
  const humidScore =
    sensor.humidity >= 30 && sensor.humidity <= 80 ? 100 : 50
  const lightScore =
    sensor.lightIntensity >= 200 && sensor.lightIntensity <= 1000 ? 100 : 50
  const soilScore =
    sensor.soilMoisture >= 20 && sensor.soilMoisture <= 80 ? 100 : 50
  const environmentalHealth = Math.round(
    (tempScore + humidScore + lightScore + soilScore) / 4
  )

  // Oxygen production score
  const oxygenProduction = Math.round(
    Math.min((sensor.o2Released / 200) * 100, 100)
  )

  // Total weighted score
  const totalScore = Math.round(
    sequestrationScore * 0.35 +
      emissionOffset * 0.25 +
      environmentalHealth * 0.25 +
      oxygenProduction * 0.15
  )

  // Net carbon balance (absorbed - emitted) in ppm
  const netCarbonBalance = sensor.co2Absorbed - sensor.co2Emitted

  // Credits earned based on score and environmental conditions
  const adjustedCredits = chaveResult.carbonCredits * envMultiplier
  const creditValueUSD = adjustedCredits * 40

  // Grade assignment
  let grade: string
  if (totalScore >= 90) grade = "A+"
  else if (totalScore >= 80) grade = "A"
  else if (totalScore >= 70) grade = "B+"
  else if (totalScore >= 60) grade = "B"
  else if (totalScore >= 50) grade = "C"
  else if (totalScore >= 40) grade = "D"
  else grade = "F"

  return {
    totalScore: Math.min(totalScore, 100),
    grade,
    breakdown: {
      sequestrationScore: Math.min(sequestrationScore, 100),
      emissionOffset: Math.min(emissionOffset, 100),
      environmentalHealth,
      oxygenProduction: Math.min(oxygenProduction, 100),
    },
    creditsEarned: Math.round(adjustedCredits * 10000) / 10000,
    creditValueUSD: Math.round(creditValueUSD * 100) / 100,
    netCarbonBalance: Math.round(netCarbonBalance * 100) / 100,
  }
}

/**
 * Generate simulated sensor data for demo/when ESP32 is disconnected
 * In production this comes from the ESP32 via WebSocket/HTTP
 */
export function generateSimulatedSensorData(): SensorData {
  const baseTemp = 26
  const baseHumidity = 62
  return {
    temperature: baseTemp + (Math.random() - 0.5) * 6,
    humidity: baseHumidity + (Math.random() - 0.5) * 20,
    soilMoisture: 45 + (Math.random() - 0.5) * 30,
    lightIntensity: 550 + (Math.random() - 0.5) * 300,
    ph: 6.5 + (Math.random() - 0.5) * 2,
    co2Emitted: 380 + Math.random() * 100,
    co2Absorbed: 350 + Math.random() * 150,
    o2Released: 180 + Math.random() * 80,
    timestamp: new Date().toISOString(),
  }
}
