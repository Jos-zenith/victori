# Quick Start: Real-time Carbon Credit Calculator

## 5-Minute Setup

### 1. ESP32 Configuration (2 minutes)

Edit `victori/ESP32_SETUP/tree_sensor_esp32.ino`:

```cpp
// Line 26-27: Update WiFi credentials
const char* ssid = "Your_WiFi_SSID";
const char* password = "Your_WiFi_Password";

// Line 30-33: Update API endpoints
const char* webhookURL = "https://your-project.supabase.co/functions/v1/receive-sensor-data";
const char* deviceID = "esp32-001";
const char* apiKey = "your-device-api-key";
```

### 2. Upload Sketch (2 minutes)

1. Open Arduino IDE
2. Go to Sketch → Include Library → Add .ZIP Library
3. Add all required libraries (ArduinoJson, DHT, BH1750, etc.)
4. Select Board: ESP32 Dev Module
5. Connect ESP32 via USB
6. Click Upload

### 3. Test Webhook (1 minute)

```bash
curl -X POST https://your-project.supabase.co/functions/v1/receive-sensor-data \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "esp32-001",
    "api_key": "your-device-api-key",
    "temperature": 28.5,
    "humidity": 65.3,
    "soil_moisture": 45.2,
    "light_intensity": 750,
    "dbh": 25.5,
    "tree_height": 18.0
  }'
```

### 4. View Dashboard

- Open the Victori app
- Navigate to Dashboard
- You should see the real-time banner with live data

## Key Metrics Explained

| Metric | Formula | Example |
|--------|---------|---------|
| **Health Score** | Avg(temp, humidity, light factors) | 87% |
| **Monthly CO₂** | Chave equation ÷ 12 | 38 kg |
| **Annual CO₂** | Monthly × 12 | 456 kg |
| **Carbon Credits** | Total CO₂ ÷ 10 | 245 credits |

## Chave Equation Reference

For a 30cm diameter tree with 20m height:

```
AGB = 0.0919 × (0.60 × 30² × 20)^0.906 ≈ 264.5 kg
Carbon = 264.5 × 0.47 ≈ 124.3 kg
CO₂ = 124.3 × 3.67 ≈ 456 kg/year
Monthly = 456 ÷ 12 ≈ 38 kg
```

## Sensor Calibration Tips

| Sensor | Calibration |
|--------|-----------|
| **DHT22** | Warm up 30 seconds before first reading |
| **BH1750** | Auto-calibrates in darkness (< 1 lux) |
| **Ultrasonic** | Measure from tree base at 1.3m height (DBH reference) |
| **Distance** | Provide manual DBH value in sketch if available |

## Troubleshooting Checklist

- [ ] ESP32 connects to WiFi (check serial monitor)
- [ ] Webhook URL is correct in sketch
- [ ] Device API key matches in webhook receiver
- [ ] Dashboard shows "Live ESP32 Data" banner
- [ ] Real-time values update every 30 seconds
- [ ] Health score is between 0-100%
- [ ] CO₂ calculation shows positive value

## File Structure

```
victori/
├── ESP32_SETUP/
│   └── tree_sensor_esp32.ino          ← Edit this file
├── src/
│   └── App.vue                         ← Dashboard (auto-updates)
└── functions/
    └── chave_calculator.py            ← Biomass calculations

supabase/
└── functions/
    ├── receive-sensor-data/index.ts   ← Webhook receiver
    └── upload-tree-image/index.ts     ← Image handler
```

## Real-time Data Flow

```
ESP32 (sends every 30s)
    ↓
Webhook (stores in Supabase)
    ↓
App.vue (Supabase subscription)
    ↓
Dashboard (updates live)
```

## Next Steps

1. ✅ Configure ESP32
2. ✅ Upload sketch
3. ✅ Test webhook
4. 🔲 Calibrate tree height sensor
5. 🔲 Connect to multiple trees
6. 🔲 Monitor dashboard

## Support

- Logs: Browser console in dashboard
- Serial monitor: Arduino IDE at 115200 baud
- Webhook status: Check Supabase function logs
- Database: View `sensor_readings` table directly in Supabase
