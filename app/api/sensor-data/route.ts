import { NextResponse } from "next/server"

// In-memory store for latest sensor readings (in production, use a database)
let latestSensorData = {
  temperature: 26.4,
  humidity: 62.5,
  soilMoisture: 47.2,
  lightIntensity: 580,
  ph: 6.8,
  co2Emitted: 412,
  co2Absorbed: 385,
  o2Released: 210,
  timestamp: new Date().toISOString(),
}

// POST: Receive data from ESP32
export async function POST(request: Request) {
  try {
    const data = await request.json()

    // Validate API key from ESP32
    const apiKey = request.headers.get("x-api-key")
    if (apiKey && apiKey !== process.env.ESP32_API_KEY && process.env.ESP32_API_KEY) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 })
    }

    // Update latest sensor data
    latestSensorData = {
      temperature: data.temperature ?? latestSensorData.temperature,
      humidity: data.humidity ?? latestSensorData.humidity,
      soilMoisture: data.soil_moisture ?? data.soilMoisture ?? latestSensorData.soilMoisture,
      lightIntensity: data.light_intensity ?? data.lightIntensity ?? latestSensorData.lightIntensity,
      ph: data.ph ?? latestSensorData.ph,
      co2Emitted: data.co2_emitted ?? data.co2Emitted ?? latestSensorData.co2Emitted,
      co2Absorbed: data.co2_absorbed ?? data.co2Absorbed ?? latestSensorData.co2Absorbed,
      o2Released: data.o2_released ?? data.o2Released ?? latestSensorData.o2Released,
      timestamp: new Date().toISOString(),
    }

    return NextResponse.json({
      success: true,
      message: "Sensor data received",
      timestamp: latestSensorData.timestamp,
    })
  } catch {
    return NextResponse.json(
      { error: "Invalid request body" },
      { status: 400 }
    )
  }
}

// GET: Return latest sensor data to the dashboard
export async function GET() {
  return NextResponse.json(latestSensorData)
}
