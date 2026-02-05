# HCCMS Cloud Functions - API Documentation

## Overview

Cloud Functions provide the backend API for the Household Carbon Credit Monitoring System. All functions are deployed to Firebase and accessible via HTTPS endpoints.

**Base URL:** `https://{REGION}-{PROJECT_ID}.cloudfunctions.net`

---

## 📝 Endpoints

### 1. Receive Sensor Data
**Endpoint:** `POST /receiveSensorData`  
**Purpose:** Accept sensor readings from Arduino/ESP32 devices and store in Firestore

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "device_id": "device_001",
    "api_key": "your_secret_api_key_here",
    "temperature": 24.5,
    "humidity": 65.0,
    "soil_moisture": 75.0,
    "light_intensity": 85.0,
    "pressure": 1013.25,
    "co2_level": 420.0,
    "battery": 95,
    "rssi": -45
}
```

**Request Field Specifications:**
| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| `device_id` | string | ✓ | — | Unique device identifier (must match registered device) |
| `api_key` | string | ✓ | — | Secret key for device authentication |
| `temperature` | float | ✓ | -50 to 60 | Temperature in Celsius |
| `humidity` | float | ✓ | 0 to 100 | Relative humidity percentage |
| `soil_moisture` | float | ✓ | 0 to 100 | Soil moisture percentage (calibrated) |
| `light_intensity` | float | ✓ | 0 to 100 | Light intensity percentage |
| `pressure` | float | ✗ | 800 to 1200 | Atmospheric pressure in hPa |
| `co2_level` | float | ✗ | 300 to 2000 | CO2 level in ppm |
| `battery` | float | ✗ | 0 to 100 | Battery level percentage (default: 100) |
| `rssi` | integer | ✗ | -120 to 0 | WiFi signal strength (default: -100) |

**Curl Example:**
```bash
curl -X POST https://us-central1-hccms-project.cloudfunctions.net/receiveSensorData \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "device_001",
    "api_key": "secret_key_12345",
    "temperature": 24.5,
    "humidity": 65.0,
    "soil_moisture": 75.0,
    "light_intensity": 85.0,
    "battery": 95,
    "rssi": -45
  }'
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Data received successfully",
    "doc_id": "2026-02-05T14:30:45.123000"
}
```

**Error Responses:**
- `400 Bad Request` - Validation failed
```json
{
    "error": "Validation failed",
    "details": [
        {
            "type": "float_parsing",
            "loc": ["temperature"],
            "msg": "Input should be a valid number"
        }
    ]
}
```

- `401 Unauthorized` - Authentication failed
```json
{
    "error": "Authentication failed"
}
```

- `500 Internal Server Error` - Server error
```json
{
    "error": "Server error: [error details]"
}
```

---

### 2. Calculate Daily Summary
**Endpoint:** `POST /calculateDailySummary`  
**Purpose:** Aggregate sensor readings for a specific date and calculate daily summary

**Request Body:**
```json
{
    "device_id": "device_001",
    "date": "2026-02-05"
}
```

**Field Specifications:**
| Field | Type | Required | Format | Description |
|-------|------|----------|--------|-------------|
| `device_id` | string | ✓ | — | Device identifier |
| `date` | string | ✗ | YYYY-MM-DD | Date to summarize (default: today) |

**Curl Example:**
```bash
curl -X POST https://us-central1-hccms-project.cloudfunctions.net/calculateDailySummary \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "device_001",
    "date": "2026-02-05"
  }'
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Daily summary calculated",
    "summary": {
        "device_id": "device_001",
        "date": "2026-02-05",
        "reading_count": 144,
        "temperature": {
            "min": 18.2,
            "max": 32.5,
            "avg": 25.3
        },
        "humidity": {
            "min": 42.0,
            "max": 78.5,
            "avg": 65.2
        },
        "soil_moisture": {
            "min": 55.0,
            "max": 88.0,
            "avg": 72.3
        },
        "light_intensity": {
            "min": 10.0,
            "max": 95.0,
            "avg": 65.0
        },
        "carbon_change_kg": 0.0785,
        "created_at": "2026-02-05T23:59:59Z"
    }
}
```

---

### 3. Get Device Summary
**Endpoint:** `GET /getDeviceSummary?device_id=XXX&days=7`  
**Purpose:** Retrieve recent daily summaries for a device

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `device_id` | string | ✓ | — | Device identifier |
| `days` | integer | ✗ | 7 | Number of days to retrieve |

**Curl Example:**
```bash
curl 'https://us-central1-hccms-project.cloudfunctions.net/getDeviceSummary?device_id=device_001&days=7'
```

**Success Response (200):**
```json
{
    "success": true,
    "device_id": "device_001",
    "summaries": [
        {
            "date": "2026-02-05",
            "data": {
                "device_id": "device_001",
                "reading_count": 144,
                "temperature": {
                    "avg": 25.3,
                    "min": 18.2,
                    "max": 32.5
                },
                "carbon_change_kg": 0.0785
                // ... more fields
            }
        },
        {
            "date": "2026-02-04",
            "data": { /* ... */ }
        }
        // ... more days
    ]
}
```

---

### 4. Health Check
**Endpoint:** `GET /healthCheck`  
**Purpose:** Simple endpoint to verify Cloud Functions are running

**Curl Example:**
```bash
curl 'https://us-central1-hccms-project.cloudfunctions.net/health_check'
```

**Success Response (200):**
```json
{
    "status": "healthy",
    "service": "HCCMS Cloud Functions",
    "timestamp": "2026-02-05T14:30:45.123456"
}
```

---

## 🔐 Authentication

### Device Authentication
Each device must have:
1. **device_id**: Unique identifier (registered in Firestore `devices` collection)
2. **api_key**: Secret key stored in device document

The API validates both before accepting sensor data.

### Future: Firebase Authentication
For frontend/dashboard access, implement Firebase Authentication:
```javascript
// Vue.js example
import { initializeApp } from 'firebase/app'
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth'

const auth = getAuth()
await signInWithEmailAndPassword(auth, email, password)
const idToken = await auth.currentUser.getIdToken()

// Use idToken in request headers:
fetch(url, {
    headers: {
        'Authorization': `Bearer ${idToken}`
    }
})
```

---

## 📊 Firestore Data Structure

### sensor_readings/{device_id}/readings/{doc_id}
```
{
    device_id: string
    user_id: string
    temperature: number
    humidity: number
    soil_moisture: number
    light_intensity: number
    battery: number
    rssi: integer
    timestamp: Timestamp (server-set)
    received_at: Timestamp
    processed: boolean
}
```

### daily_summaries/{device_id}/summaries/{date}
```
{
    device_id: string
    date: string (YYYY-MM-DD)
    reading_count: number
    temperature: {min, max, avg}
    humidity: {min, max, avg}
    soil_moisture: {min, max, avg}
    light_intensity: {min, max, avg}
    carbon_change_kg: number
    created_at: Timestamp
}
```

---

## 🚀 Deployment

### Prerequisites
- Firebase project with Firestore enabled
- Firebase CLI installed: `npm install -g firebase-tools`
- Service account credentials

### Deploy Steps

```bash
# 1. Navigate to functions directory
cd victori/functions

# 2. Authenticate with Firebase
firebase login

# 3. Select your Firebase project
firebase use your-project-id

# 4. Deploy functions
firebase deploy --only functions

# 5. View deployment logs
firebase functions:log

# 6. Get function URLs
firebase functions:list
```

### Environment Variables
Create a `.env` file or set via Firebase console:
```
CARBON_RATE_KG_PER_CREDIT=1.0
CARBON_CREDIT_VALUE_USD=15.00
```

---

## 🧪 Testing Endpoints Locally

### Start emulator
```bash
firebase emulators:start --only functions
```

### Test in another terminal
```bash
curl -X POST http://localhost:5001/your-project-id/us-central1/receiveSensorData \
  -H 'Content-Type: application/json' \
  -d '{"device_id":"device_001","api_key":"test_key",...}'
```

---

## ⚠️ Error Codes

| Code | Message | Cause |
|------|---------|-------|
| 400 | Invalid JSON | Malformed request body |
| 400 | Validation failed | Field values out of range |
| 401 | Authentication failed | Invalid device_id or api_key |
| 404 | No readings found | No data for specified date |
| 500 | Server error | Firestore/system error |

---

## 📈 Monitoring

### Check Cloud Function Logs
```bash
firebase functions:log
```

### Firestore Activity
- View in Firebase Console → Firestore Database → Database → Logs
- Monitor `sensor_readings`, `daily_summaries`, `activity_logs` collections

### Performance Tips
- Batch sensor reads (send every 10 minutes instead of continuous)
- Regular cleanup of old sensor readings (>90 days)
- Use indexed queries for faster reads

---

## 🔗 Integration Example (Arduino/ESP32)

```cpp
// Arduino sketch pseudocode
#include <HTTPClient.h>
#include <ArduinoJson.h>

void sendSensorData(float temp, float humidity, ...) {
    WiFiClient client;
    HTTPClient http;
    
    String serverUrl = "https://us-central1-project-id.cloudfunctions.net/receiveSensorData";
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    DynamicJsonDocument doc(200);
    doc["device_id"] = "device_001";
    doc["api_key"] = "secret_key";
    doc["temperature"] = temp;
    doc["humidity"] = humidity;
    // ... add other fields
    
    String payload;
    serializeJson(doc, payload);
    
    int httpCode = http.POST(payload);
    if (httpCode == 201) {
        Serial.println("Data sent successfully");
    }
    
    http.end();
}
```

---

## 📞 Support

For issues or questions:
- Check Cloud Function logs: `firebase functions:log`
- Verify Firestore rules and indexes
- Ensure device is registered in Firestore
- Check device api_key matches exactly
