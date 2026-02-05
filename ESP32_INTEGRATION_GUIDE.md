# ESP32 Carbon Credit Tree Sensor Integration Guide

## Overview

This guide explains how to connect your ESP32 microcontroller with sensors and ESP32-CAM to the Victori Carbon Credit Calculator for real-time tree monitoring and biomass calculation using the Chave allometric equation.

## System Architecture

```
ESP32 + Sensors → Webhook → Supabase Edge Functions → Dashboard
                  (every 30s)
                           ↓
                    Chave Equation
                    Calculations
                           ↓
                  Real-time Updates
                   (Supabase Subs)
```

## Hardware Requirements

### Essential Components
1. **ESP32 Development Board**
   - WiFi-enabled microcontroller
   - 3.3V logic level
   - GPIO pins available

2. **Sensors**
   - **DHT22**: Temperature & Humidity
     - Pin: GPIO 4
     - I2C/Single-wire protocol
   
   - **BH1750**: Light Intensity
     - Pin: GPIO 21 (SDA), GPIO 22 (SCL)
     - I2C protocol
     - Measures in lux, converts to µmol/m²/s
   
   - **MQ135**: CO2 Level
     - Pin: GPIO 34 (ADC)
     - Analog output
   
   - **HC-SR04**: Ultrasonic Distance (Tree Height)
     - TRIG: GPIO 18
     - ECHO: GPIO 5

### Optional - Image Capture
3. **ESP32-CAM Module**
   - OV2640 camera
   - Dedicated board with flash
   - Enables tree identification

## Wiring Diagram

```
ESP32 DevKit
├── VCC → 5V Power Supply
├── GND → Ground
├── GPIO 4 (DHT22) → DHT22 Data Pin
├── GPIO 21/22 (I2C) → BH1750 SDA/SCL
├── GPIO 34 (MQ135) → MQ135 Analog Out
├── GPIO 18 (HC-SR04) → TRIG Pin
├── GPIO 5 (HC-SR04) → ECHO Pin
└── GPIO 2 (LED) → Optional Status LED

Power:
- 5V/3A USB-C or external power adapter
- Capacitor: 100µF across power rails
```

## Software Setup

### 1. Arduino IDE Configuration

1. Install Arduino IDE 2.0+
2. Add ESP32 board manager:
   - File → Preferences
   - Boards Manager URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Add to Additional Boards Manager URLs

3. Install ESP32 board package:
   - Boards Manager → Search "ESP32" → Install latest version

### 2. Required Libraries

Install these libraries via Library Manager:

```
- DHT sensor library by Adafruit
- BH1750 by Christopher Laws
- ArduinoJson by Benoit Blanchon
- AsyncHTTPClient (for ESP32)
```

Installation steps:
1. Sketch → Include Library → Manage Libraries
2. Search each library name
3. Install the latest version

### 3. Configure Your Sketch

Edit the following in `tree_sensor_esp32.ino`:

```cpp
// WiFi Credentials
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// API Configuration
const char* webhookURL = "https://your-project.supabase.co/functions/v1/receive-sensor-data";
const char* imageUploadURL = "https://your-project.supabase.co/functions/v1/upload-tree-image";
const char* deviceID = "esp32-001";        // Unique device identifier
const char* apiKey = "your-device-api-key"; // Get from Supabase dashboard
```

### 4. Get Supabase Credentials

1. Log into your Supabase project
2. Navigate to Settings → API
3. Copy:
   - **Project URL**: Use as `https://your-project.supabase.co`
   - **Service Role Key**: For backend operations (keep secret)
   - **Anon Key**: For frontend (can be public)

4. Create device API key in Supabase:
   ```sql
   -- Insert your ESP32 device
   INSERT INTO devices (
     id, user_id, name, device_type, 
     api_key, status, location, sensors
   ) VALUES (
     'esp32-001',
     (SELECT id FROM users LIMIT 1),
     'Tree 1 Sensor Node',
     'esp32',
     'your-device-api-key',
     'active',
     '{"latitude": 0, "longitude": 0}',
     '{"temperature": true, "humidity": true, "light": true, "co2": true, "height": true}'
   );
   ```

### 5. Upload to ESP32

1. Select board:
   - Tools → Board → ESP32 → ESP32 Dev Module

2. Select port:
   - Tools → Port → COM#

3. Set upload speed:
   - Tools → Upload Speed → 921600

4. Upload:
   - Sketch → Upload

## Real-Time Data Flow

### Sensor Reading Cycle (Every 5 seconds)

```
Read Temperature/Humidity (DHT22)
  ↓
Read Light Intensity (BH1750)
  ↓
Read CO2 Level (MQ135)
  ↓
Measure Tree Height (HC-SR04)
  ↓
Calculate CO2 Absorption Rate
  ↓
Store in Memory
```

### Webhook Transmission (Every 30 seconds)

```json
{
  "device_id": "esp32-001",
  "api_key": "your-device-api-key",
  "temperature": 26.5,
  "humidity": 75.2,
  "soil_moisture": 50.0,
  "light_intensity": 850.0,
  "co2_level": 420.0,
  "battery": 85,
  "rssi": -45,
  "dbh": 30.5,
  "tree_height": 25.0,
  "co2_emitted_ppm": 420.0,
  "co2_absorbed_ppm": 25.5,
  "o2_released_ppm": 18.2
}
```

### Server-Side Processing

1. **Validation**: Verify device authentication
2. **Storage**: Insert sensor reading into database
3. **Calculation**: Apply Chave equation
   ```
   AGB = 0.0919 × (ρ × DBH² × H)^0.906
   Carbon = AGB × 0.47
   CO2 = Carbon × 3.67
   ```
4. **Broadcast**: Emit real-time update to dashboard
5. **Aggregation**: Update daily carbon credits

### Dashboard Update (Real-time)

The Vue dashboard subscribes to:
- `sensor_readings` table changes
- `tree_identifications` table changes
- Receives updates every 30 seconds
- Calculates health score dynamically
- Updates metrics in real-time

## Chave Equation Implementation

The system uses the **Chave allometric equation** for above-ground biomass (AGB) estimation:

### Formula

For moist tropical forests (default):
```
AGB = 0.0919 × (ρ × DBH² × H)^0.906
```

Where:
- **AGB**: Above-Ground Biomass (kg)
- **ρ (rho)**: Wood density (g/cm³)
- **DBH**: Diameter at Breast Height (cm) - at 1.3m height
- **H**: Tree height (m)

### Carbon Conversion

```
Carbon = AGB × 0.47  (47% of dry biomass is carbon)
CO₂ = Carbon × 3.67  (molecular weight ratio)
Monthly CO₂ = Annual CO₂ / 12
```

### Wood Density by Species

Common values used in calculations:
- Shorea robusta (Sal): 0.80 g/cm³
- Mango: 0.62 g/cm³
- Eucalyptus: 0.65 g/cm³
- Oak: 0.75 g/cm³
- Default: 0.60 g/cm³

## Measuring DBH Accurately

DBH (Diameter at Breast Height) must be measured at **1.3 meters** from the ground:

### Option 1: Manual Measurement
1. Use a measuring tape around the trunk
2. Divide circumference by π (3.14159) to get diameter
3. Record value in centimeters

### Option 2: Image Analysis
1. Capture tree image with ESP32-CAM
2. System analyzes bark texture and trunk width
3. ML model estimates DBH from image features
4. Manual verification recommended

### Option 3: Ultrasonic Estimation
The ESP32 sketch includes HC-SR04 for height measurement.
For DBH, use a reference object in frame and calculate ratio.

## Troubleshooting

### Issue: ESP32 Won't Connect to WiFi

**Solution:**
```cpp
// Check WiFi credentials
Serial.println(ssid);
Serial.println(password);

// Try 5GHz disabled
WiFi.mode(WIFI_STA);
WiFi.begin(ssid, password);
```

### Issue: Sensor Readings are 0 or Invalid

**Solution:**
- Check I2C connections (BH1750)
- Verify DHT pin (GPIO 4) is not pulled low
- Check power supply voltage (3.3V)
- Run `scanI2CDevices()` to verify I2C addresses

### Issue: Webhook Returns 401 Unauthorized

**Solution:**
- Verify device ID exists in Supabase database
- Check API key matches database record
- Confirm device status is 'active'
- Check Supabase RLS policies allow device access

### Issue: Real-time Dashboard Updates Not Working

**Solution:**
- Check Supabase real-time is enabled
  - Settings → Replication → Enable for tables
- Verify Vue.js subscriptions are initialized
- Check browser console for WebSocket errors
- Confirm environment variables in .env

## Performance Optimization

### Reduce Data Size
- Send readings every 30 seconds (vs 5 second reads)
- Store average values, not individual readings
- Compress image to <100KB before upload

### Optimize Battery Life
- Reduce LED brightness
- Use deep sleep between readings
- Disable WiFi during sensor reads
- Lower camera frame rate

### Database Efficiency
- Create indices on `device_id` and `timestamp`
- Archive old readings monthly
- Use materialized views for aggregates
- Batch inserts when possible

## Example Data Flow

```
Time: 10:00:00 - Sensors Read
├── Temp: 26.5°C
├── Humidity: 75.2%
├── Light: 850 µmol/m²/s
├── Height: 25m
├── DBH: 30.5cm
└── CO2: 420ppm

Time: 10:00:30 - Webhook Sent
├── POST /receive-sensor-data
├── Response: {"success": true, "reading_id": "uuid"}
└── Inserted to sensor_readings table

Time: 10:00:30 - Real-time Update
├── Supabase broadcast to websocket
├── Vue dashboard receives update
├── Calculations:
│   ├── AGB = 0.0919 × (0.60 × 30.5² × 25)^0.906 = 582 kg
│   ├── Carbon = 582 × 0.47 = 274 kg
│   ├── CO₂ = 274 × 3.67 = 1,005 kg/year
│   └── Monthly = 84 kg CO₂
└── Dashboard metrics update

Time: 10:00:35 - Image Capture (every 5 mins)
├── ESP32-CAM captures trunk image
├── Converts to base64
├── POST /upload-tree-image
├── ML model identifies species
└── Updates carbon rates

Time: 10:01:00 - Next Cycle
└── Repeats...
```

## Advanced: Custom Forest Types

Modify Chave coefficients for your region:

```python
# In chave_calculator.py
CHAVE_COEFFICIENTS = {
    ForestType.WET: {"a": 0.0673, "b": 0.976},    # Wet tropical
    ForestType.MOIST: {"a": 0.0919, "b": 0.906},  # Moist tropical (DEFAULT)
    ForestType.DRY: {"a": 0.0919, "b": 0.906},    # Dry tropical
    ForestType.TEMPERATE: {"a": 0.0549, "b": 0.995},  # Temperate
}
```

Select during calculation:
```python
result = ChaveCalculator.calculate_agb(
    dbh=30.5,
    height=25.0,
    species="Shorea robusta",
    forest_type=ForestType.MOIST  # Change as needed
)
```

## Next Steps

1. ✅ Flash ESP32 with provided sketch
2. ✅ Set up sensors and wiring
3. ✅ Configure WiFi and API keys
4. ✅ Verify webhook data in Supabase dashboard
5. ✅ Check real-time updates on Vue dashboard
6. ✅ Measure DBH and update database
7. ✅ Monitor carbon calculations
8. ✅ Capture tree images for ML identification

## Support Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Chave Equation Reference](https://www.globalforestwatch.org)
- [ESP32 Documentation](https://docs.espressif.com)
- [Victori GitHub Issues](https://github.com/Jos-zenith/victori/issues)

---

**Last Updated**: February 2026
**Version**: 1.0
