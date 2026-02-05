# Real-time ESP32 Carbon Credit Calculator Integration

## Overview

This guide explains how to integrate your ESP32 with the Victori Carbon Credit Calculator to capture real-time tree sensor data and automatically calculate carbon offset using the **Chave allometric equation**.

## System Architecture

```
ESP32 (with sensors + camera)
    ↓
    └─→ Captures: Temperature, Humidity, Light, DBH, Height, Images
    
        ↓
        
Webhook Endpoint (receive-sensor-data)
    ↓
    └─→ Receives tree measurements
    └─→ Stores in Supabase (with metadata)
    
        ↓
        
Real-time Subscriptions (App.vue)
    ↓
    └─→ Displays live sensor data
    └─→ Calculates Chave biomass & CO2
    └─→ Updates dashboard in real-time
    
        ↓
        
Tree Image Upload Handler (upload-tree-image)
    ↓
    └─→ Receives ESP32 CAM images
    └─→ Stores in Supabase Storage
    └─→ Triggers tree species identification
```

## Chave Allometric Equation

The Chave equation is used to calculate Above Ground Biomass (AGB) from tree measurements:

$$AGB = 0.0919 \times (\rho \times DBH^2 \times H)^{0.906}$$

Where:
- **ρ (rho)** = Wood density (default: 0.60 g/cm³)
- **DBH** = Diameter at Breast Height (in cm)
- **H** = Tree height (in meters)

### CO₂ Conversion:
1. Carbon content = AGB × 0.47 (47% of dry biomass)
2. CO₂ equivalent = Carbon × 3.67 (molecular weight conversion)
3. Monthly rate = CO₂ / 12

### Example Calculation:
- DBH: 30cm, Height: 20m, Wood Density: 0.60
- AGB = 0.0919 × (0.60 × 30² × 20)^0.906 ≈ 264.5 kg
- Carbon = 264.5 × 0.47 ≈ 124.3 kg
- CO₂ = 124.3 × 3.67 ≈ 456 kg/year ≈ 38 kg/month

## ESP32 Hardware Setup

### Required Components:
- ESP32 DevKit
- Temperature & Humidity Sensor (DHT22 or BME280)
- Light Intensity Sensor (BH1750 or similar)
- Distance Sensor (VL53L0X or similar for tree height estimation)
- ESP32-CAM (for tree image capture)
- WiFi connectivity

### Pin Configuration:
```
Temperature/Humidity (DHT22): GPIO 4
Light Sensor (BH1750):        GPIO 21 (SDA), GPIO 22 (SCL)
Distance Sensor (VL53L0X):   GPIO 21 (SDA), GPIO 22 (SCL)
Camera (ESP32-CAM):           Pre-configured on module
```

### Arduino Sketch Setup:

1. **Install Required Libraries:**
   ```
   - ArduinoJson
   - DHT
   - BH1750
   - VL53L0X
   - esp32-camera (for CAM module)
   ```

2. **Configure WiFi Credentials:**
   Edit the sketch and update:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   const char* webhookURL = "https://your-project.supabase.co/functions/v1/receive-sensor-data";
   const char* apiKey = "YOUR_API_KEY"; // Device API key from Supabase
   ```

3. **Set Device ID:**
   ```cpp
   const char* deviceId = "esp32-tree-001"; // Unique identifier for this ESP32
   ```

4. **Upload Sketch:**
   - Use Arduino IDE with ESP32 board support
   - Select correct board and COM port
   - Upload the provided `tree_sensor_esp32.ino` sketch

## Data Flow & Sensor Fields

### Sensor Data Payload (JSON):
```json
{
  "device_id": "esp32-tree-001",
  "api_key": "your-device-key",
  "temperature": 28.5,
  "humidity": 65.3,
  "soil_moisture": 45.2,
  "light_intensity": 750,
  "pressure": 1013.25,
  "co2_level": 420,
  "battery": 95,
  "rssi": -58,
  "dbh": 25.5,
  "tree_height": 18.0,
  "co2_emitted_ppm": 425,
  "co2_absorbed_ppm": 50,
  "o2_released_ppm": 180,
  "tree_species": "Mango Tree"
}
```

### Stored in Metadata (Existing Schema):
Tree measurement data is stored in the `metadata` JSON field of `sensor_readings`:
```json
{
  "metadata": {
    "tree_dbh": 25.5,
    "tree_height": 18.0,
    "co2_emitted_ppm": 425,
    "co2_absorbed_ppm": 50,
    "o2_released_ppm": 180,
    "tree_species": "Mango Tree"
  }
}
```

## Dashboard Real-time Updates

The Vue dashboard automatically:

1. **Subscribes to sensor_readings changes** via Supabase Real-time API
2. **Extracts tree data from metadata** field
3. **Calculates Chave biomass & CO₂** using the equation
4. **Computes health score** based on environmental factors
5. **Updates live banner** with sensor readings

### Health Score Calculation:

```javascript
const calculateHealthScore = (temp, humidity, lightIntensity) => {
  const optimalTemp = 25°C
  const optimalHumidity = 70%
  const optimalLight = 800 µmol/m²/s
  
  // Normalized deviation from optimal values
  const tempFactor = 1 - |temp - 25| / 40
  const humidityFactor = 1 - |humidity - 70| / 50
  const lightFactor = 1 - |lightIntensity - 800| / 1000
  
  // Average of all factors (0-100%)
  Score = (tempFactor + humidityFactor + lightFactor) / 3
}
```

## Image Capture & Analysis

### ESP32 CAM Setup:

1. **Program ESP32-CAM Module:**
   - Use Arduino IDE with AI-Thinker ESP32-CAM board selected
   - Upload `esp32_cam_capture.ino` sketch

2. **Image Upload Endpoint:**
   The `/upload-tree-image` function:
   - Receives image from ESP32-CAM
   - Uploads to Supabase Storage at `/tree-images/{device_id}/{timestamp}.jpg`
   - Triggers ML inference for tree species identification
   - Stores results in `tree_identifications` table

3. **Upload Code (ESP32-CAM):**
   ```cpp
   // Capture frame from camera
   camera_fb_t * fb = esp_camera_fb_get();
   
   // Send to upload endpoint
   httpClient.beginRequest();
   httpClient.post("https://your-project.supabase.co/functions/v1/upload-tree-image");
   httpClient.sendHeader("Content-Type", "multipart/form-data");
   httpClient.sendHeader("Authorization", "Bearer " + apiKey);
   httpClient.write(fb->buf, fb->len);
   httpClient.endRequest();
   ```

## Webhook Testing

### Test with cURL:
```bash
curl -X POST https://your-project.supabase.co/functions/v1/receive-sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "esp32-tree-001",
    "api_key": "your-api-key",
    "temperature": 28.5,
    "humidity": 65.3,
    "soil_moisture": 45.2,
    "light_intensity": 750,
    "dbh": 25.5,
    "tree_height": 18.0,
    "co2_emitted_ppm": 425,
    "co2_absorbed_ppm": 50,
    "o2_released_ppm": 180
  }'
```

### Test with Postman:
1. Create new POST request
2. URL: `https://your-project.supabase.co/functions/v1/receive-sensor-data`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON): [See cURL example above]
5. Click Send

## Dashboard Features

### Real-time Banner (when data is received):
- Shows live temperature, humidity, light intensity
- Displays DBH and height measurements
- Shows calculated health score (0-100%)
- Shows monthly CO₂ offset from Chave equation

### Metric Cards:
- **Total Trees**: Running count of identified trees
- **Total CO₂ Offset**: Cumulative annual CO₂ offset in kg
- **This Month**: Monthly CO₂ offset progress bar
- **Credits Earned**: Carbon credits (1 credit = 10kg CO₂)

### Recent Identifications:
- Shows latest tree species identified
- Displays confidence level from ML model
- Timestamp of identification

## Troubleshooting

### ESP32 Won't Connect to WiFi:
- Check SSID/password in sketch
- Verify WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
- Check signal strength with `rssi` value (should be > -80)

### No Real-time Data Appearing:
- Verify webhook URL is correct in ESP32 sketch
- Check Supabase project has real-time enabled for `sensor_readings` table
- Monitor browser console for Supabase subscription errors
- Test webhook with cURL command above

### Chave Calculation Shows 0:
- Ensure DBH value is being sent from ESP32
- Check that DBH > 0 (minimum diameter required)
- Verify tree height is not 0 (uses default 20m if not provided)

### Images Not Uploading:
- Verify ESP32-CAM is programmed correctly
- Check Supabase Storage has public access enabled
- Monitor function logs in Supabase dashboard
- Ensure image file size is < 25MB

## File Locations

- **Arduino Sketch**: `/victori/ESP32_SETUP/tree_sensor_esp32.ino`
- **Chave Calculator**: `/victori/functions/chave_calculator.py`
- **Webhook Handler**: `/supabase/functions/receive-sensor-data/index.ts`
- **Image Upload**: `/supabase/functions/upload-tree-image/index.ts`
- **Vue Dashboard**: `/victori/src/App.vue`

## Next Steps

1. Assemble ESP32 hardware with sensors
2. Upload Arduino sketch to ESP32
3. Configure WiFi and webhook URL in sketch
4. Deploy Supabase functions
5. Open dashboard and verify real-time data flow
6. Capture tree images with ESP32-CAM
7. Monitor CO₂ offset calculations
