# Implementation Summary: Real-time ESP32 Carbon Credit Calculator

## What Has Been Implemented

### 1. Chave Allometric Equation Integration
- **File**: `victori/functions/chave_calculator.py` (also embedded in App.vue)
- **Equation**: `AGB = 0.0919 × (ρ × DBH² × H)^0.906`
- **Features**:
  - Calculates above-ground biomass from tree diameter (DBH) and height
  - Converts biomass to carbon content (47% of dry biomass)
  - Converts carbon to CO₂ equivalent using 3.67 factor
  - Calculates monthly offset by dividing annual by 12

### 2. Real-time Sensor Data Collection
- **File**: `supabase/functions/receive-sensor-data/index.ts`
- **Data Payload**:
  ```json
  {
    "device_id": "esp32-001",
    "api_key": "your-api-key",
    "temperature": 28.5,
    "humidity": 65.3,
    "light_intensity": 750,
    "dbh": 25.5,
    "tree_height": 18.0,
    "co2_emitted_ppm": 425,
    "co2_absorbed_ppm": 50,
    "o2_released_ppm": 180
  }
  ```
- **Storage**: Stored in `sensor_readings` table with tree data in `metadata` JSON field
- **Webhook Endpoint**: `https://your-project.supabase.co/functions/v1/receive-sensor-data`

### 3. Real-time Dashboard Updates
- **File**: `victori/src/App.vue`
- **Features**:
  - Supabase real-time subscriptions to `sensor_readings` table
  - Automatic Chave calculation when new data arrives
  - Health score computation based on temperature, humidity, light
  - Live banner showing current sensor values
  - Auto-updating metric cards for CO₂ offset tracking

### 4. Tree Image Analysis
- **File**: `supabase/functions/upload-tree-image/index.ts`
- **Flow**:
  - ESP32-CAM captures tree image
  - Uploads to Supabase Storage
  - Triggers ML inference for species identification
  - Stores results in `tree_identifications` table
  - Real-time update in dashboard

### 5. ESP32 Arduino Integration
- **File**: `victori/ESP32_SETUP/tree_sensor_esp32.ino`
- **Features**:
  - DHT22 sensor for temperature/humidity
  - BH1750 sensor for light intensity
  - MQ135 sensor for CO2 levels
  - Ultrasonic sensor for tree height estimation
  - ESP32-CAM integration for image capture
  - Automatic webhook transmission every 30 seconds

### 6. Documentation & Testing Tools
- **REALTIME_ESP32_SETUP.md**: Complete integration guide
- **QUICKSTART.md**: 5-minute setup instructions
- **test_chave.py**: Python utility to test calculations locally
- **victori/functions/chave_calculator.py**: Standalone Python module

## Chave Equation Reference

### The Mathematics
For a tree with:
- DBH = 30 cm
- Height = 20 m  
- Wood density = 0.60 g/cm³

**Step 1 - Calculate AGB:**
```
AGB = 0.0919 × (0.60 × 30² × 20)^0.906
AGB = 0.0919 × (108,000)^0.906
AGB ≈ 264.5 kg
```

**Step 2 - Carbon Content:**
```
Carbon = 264.5 × 0.47 ≈ 124.3 kg
```

**Step 3 - CO₂ Equivalent:**
```
CO₂ Annual = 124.3 × 3.67 ≈ 456 kg/year
CO₂ Monthly = 456 ÷ 12 ≈ 38 kg/month
```

**Step 4 - Carbon Credits:**
```
Credits = 456 ÷ 10 ≈ 46 credits (1 credit = 10kg CO₂)
```

## Health Score Calculation

The dashboard calculates a health score (0-100%) based on environmental conditions:

```javascript
optimalTemp = 25°C
optimalHumidity = 70%
optimalLight = 800 µmol/m²/s

tempFactor = 1 - |temperature - 25| / 40
humidityFactor = 1 - |humidity - 70| / 50
lightFactor = 1 - |lightIntensity - 800| / 1000

healthScore = (tempFactor + humidityFactor + lightFactor) / 3 * 100
```

## Real-time Data Architecture

```
┌─────────────────────────────────────────┐
│         ESP32 Microcontroller           │
│  (sensors + WiFi + optional camera)     │
└──────────────┬──────────────────────────┘
               │ HTTP POST (every 30s)
               │ Sensor data + tree measurements
               ▼
┌─────────────────────────────────────────┐
│    Supabase Edge Function (Webhook)     │
│  receive-sensor-data/index.ts           │
│  - Validates API key                    │
│  - Stores in sensor_readings table      │
│  - Tree data in metadata field          │
└──────────────┬──────────────────────────┘
               │ Real-time PostgreSQL change
               │ (broadcast via Supabase)
               ▼
┌─────────────────────────────────────────┐
│       Vue Dashboard (App.vue)            │
│  - Supabase real-time subscription      │
│  - Executes Chave calculation           │
│  - Computes health score                │
│  - Updates live banner + metrics        │
└─────────────────────────────────────────┘
```

## Database Schema

### sensor_readings Table
```sql
- id (UUID, primary key)
- device_id (string) - ESP32 identifier
- user_id (UUID) - User who owns device
- temperature (float)
- humidity (float)
- soil_moisture (float)
- light_intensity (float)
- co2_level (float, optional)
- battery (float)
- rssi (float) - WiFi signal strength
- metadata (JSON) - Tree measurements
  {
    tree_dbh: number,
    tree_height: number,
    co2_emitted_ppm: number,
    co2_absorbed_ppm: number,
    o2_released_ppm: number,
    tree_species: string
  }
- timestamp (datetime)
- received_at (datetime)
- processed (boolean)
```

### tree_identifications Table
```sql
- id (UUID, primary key)
- device_id (string)
- user_id (UUID)
- species (string) - Identified species
- confidence (float) - ML confidence (0-1)
- carbon_rate_kg_per_month (float)
- image_url (string) - Supabase Storage URL
- created_at (datetime)
```

## Configuration Files

### ESP32 Sketch Configuration
Edit `victori/ESP32_SETUP/tree_sensor_esp32.ino`:
- Lines 26-27: WiFi SSID and password
- Lines 30-33: Webhook URL, device ID, API key
- Lines 35-41: Sensor pin assignments
- Lines 57-59: Data collection intervals

### Dashboard Configuration
In `victori/src/App.vue`:
- Lines 41-44: Supabase project credentials
- Lines 47-69: Chave calculation and health score logic
- Lines 83-162: Real-time subscription handlers

## Testing the Implementation

### 1. Local Calculation Test
```bash
python victori/functions/test_chave.py --dbh 30 --height 20 --species mango
```

### 2. Webhook Test
```bash
curl -X POST https://your-project.supabase.co/functions/v1/receive-sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "esp32-001",
    "api_key": "your-api-key",
    "temperature": 28.5,
    "humidity": 65.3,
    "soil_moisture": 45.2,
    "light_intensity": 750,
    "dbh": 25.5,
    "tree_height": 18.0
  }'
```

### 3. Dashboard Real-time Test
1. Open app in browser
2. Check dashboard for "Live ESP32 Data" banner
3. Verify metric cards update every 30 seconds
4. Confirm health score is 0-100%
5. Check CO₂ calculation matches manual Chave calculation

## Files Modified/Created

### New Files
- ✅ `victori/functions/chave_calculator.py` - Biomass calculator
- ✅ `victori/ESP32_SETUP/tree_sensor_esp32.ino` - ESP32 sketch
- ✅ `victori/functions/test_chave.py` - Testing utility
- ✅ `supabase/functions/upload-tree-image/index.ts` - Image upload handler
- ✅ `REALTIME_ESP32_SETUP.md` - Full integration guide
- ✅ `QUICKSTART.md` - Quick start instructions
- ✅ `IMPLEMENTATION_SUMMARY.md` - This file

### Modified Files
- ✅ `supabase/functions/receive-sensor-data/index.ts` - Updated sensor handler
- ✅ `victori/src/App.vue` - Enhanced dashboard with real-time subscriptions

## Next Steps for Users

1. **Configure ESP32**:
   - Edit WiFi credentials in sketch
   - Add Supabase endpoints
   - Assemble sensors

2. **Upload Firmware**:
   - Use Arduino IDE
   - Select ESP32 board
   - Upload sketch

3. **Deploy Functions**:
   - Deploy receive-sensor-data function
   - Deploy upload-tree-image function
   - Configure permissions in Supabase

4. **Test Integration**:
   - Run webhook test via cURL
   - Monitor dashboard for live data
   - Verify calculations

5. **Scale Up**:
   - Connect multiple ESP32s
   - Add different tree types
   - Monitor carbon offsets over time

## Key Equations Summary

| Component | Equation | Result |
|-----------|----------|--------|
| AGB | 0.0919 × (ρ × DBH² × H)^0.906 | kg |
| Carbon | AGB × 0.47 | kg |
| CO₂ Annual | Carbon × 3.67 | kg/year |
| CO₂ Monthly | CO₂ Annual ÷ 12 | kg/month |
| Health Score | (TempF + HumF + LightF) / 3 | 0-1 (0-100%) |
| Credits | CO₂ Annual ÷ 10 | units |

## Support Resources

- **Arduino Setup**: See `victori/ESP32_SETUP/tree_sensor_esp32.ino` comments
- **API Endpoints**: See `supabase/functions/receive-sensor-data/` and `upload-tree-image/`
- **Dashboard Logic**: See `victori/src/App.vue` (lines 46-162)
- **Local Testing**: Run `python victori/functions/test_chave.py`
- **Documentation**: Read `REALTIME_ESP32_SETUP.md` and `QUICKSTART.md`

## Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| Real-time banner not showing | Check Supabase subscription in browser console |
| CO₂ calculation shows 0 | Ensure DBH > 0 in sensor data |
| Health score is 0% | Check if environmental values are outside optimal ranges |
| No webhook data received | Verify API key and webhook URL in ESP32 sketch |
| Images not uploading | Check ESP32-CAM pin configuration and Supabase Storage permissions |
