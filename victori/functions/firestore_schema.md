# HCCMS Firestore Database Schema

## Collection Structure

### 1. `users/` Collection
Stores user account information
```
users/{userId}
├── email: string
├── full_name: string
├── phone: string
├── address: {
│   street: string
│   city: string
│   state: string
│   zip: string
│   country: string,
│   latitude: number,
│   longitude: number
│}
├── account_type: string ["individual", "organization"]
├── carbon_tier: string ["bronze", "silver", "gold", "platinum"]
├── created_at: Timestamp
├── updated_at: Timestamp
└── is_active: boolean
```

---

### 2. `devices/` Collection
Stores registered hardware devices (ESP32/Arduino nodes)
```
devices/{deviceId}
├── user_id: string (reference to users collection)
├── name: string (e.g., "Front Yard Monitor", "Backyard Plant 1")
├── device_type: string ["esp32", "arduino", "other"]
├── firmware_version: string
├── serial_number: string
├── location: {
│   latitude: number
│   longitude: number
│   coordinates: GeoPoint
│   address: string
│}
├── sensors: {
│   temperature: boolean
│   humidity: boolean
│   soil_moisture: boolean
│   light_intensity: boolean
│   co2: boolean
│}
├── status: string ["active", "inactive", "error", "maintenance"]
├── last_heartbeat: Timestamp
├── battery_level: number (0-100)
├── pairs: map of {
│   sensor_name: {
│       pin: number,
│       calibration: {}
│   }
│}
├── created_at: Timestamp
├── updated_at: Timestamp
└── timezone: string
```

---

### 3. `sensor_readings/{deviceId}/` Sub-collection
Stores raw sensor data with auto-generated document IDs by timestamp
```
sensor_readings/{deviceId}/{timestamp_doc}
├── temperature: number (Celsius)
├── humidity: number (0-100 %)
├── soil_moisture: number (0-100 %)
├── light_intensity: number (0-100 %)
├── pressure: number (optional, hPa)
├── co2_level: number (optional, ppm)
├── rssi: number (WiFi signal strength)
├── battery: number (%)
├── device_id: string
├── user_id: string
├── timestamp: Timestamp (server-set)
├── received_at: Timestamp
└── processed: boolean
```

**Indexing Strategy:**
- Compound index on: `device_id`, `timestamp` (DESC) - for recent readings
- TTL: Set to 90 days for cost efficiency (optional)

---

### 4. `tree_identifications/` Collection
Stores tree species identification results from ML model
```
tree_identifications/{identificationId}
├── device_id: string
├── user_id: string
├── image_url: string (Firebase Storage reference)
├── species: string (e.g., "Shorea robusta", "Pinus roxburghii")
├── confidence: number (0-1, confidence score from model)
├── processing_time_ms: number
├── model_version: string
├── identified_at: Timestamp
├── metadata: {
│   tree_age_estimate: string (optional)
│   tree_height_estimate: number (optional)
│   tree_health_status: string ["healthy", "stressed", "diseased"]
│}
└── model_details: {
    model_name: string
    framework: string ("pytorch")
}
```

---

### 5. `carbon_credits/{monthKey}/` Sub-collection
Stores monthly aggregated carbon credit calculations
```
carbon_credits/{userId}/{monthKey}
├── user_id: string
├── device_id: string
├── year: number (2026)
├── month: number (1-12)
├── month_key: string (e.g., "2026-01")
├── sensor_data_points: number (total readings)
├── avg_temperature: number
├── avg_humidity: number
├── avg_soil_moisture: number
├── tree_species: [array of identified species]
├── carbon_absorbed_kg: number
├── carbon_sequestration_rate: number (kg/month)
├── vehicle_emissions_offset: {
│   kg_offset: number
│   miles_equivalent: number (how many car miles offset)
│}
├── carbon_credits_earned: number
├── credit_value_usd: number (at current rate)
├── verification_status: string ["pending", "verified", "disputed"]
├── calculation_method: string
├── created_at: Timestamp
└── updated_at: Timestamp
```

---

### 6. `daily_summaries/{deviceId}/` Sub-collection
Stores daily aggregated metrics (faster queries than raw readings)
```
daily_summaries/{deviceId}/{dateKey}
├── device_id: string
├── date: string ("2026-02-05")
├── date_key: string (same as dateKey)
├── reading_count: number
├── temperature: {
│   min: number
│   max: number
│   avg: number
│}
├── humidity: {
│   min: number
│   max: number
│   avg: number
│}
├── soil_moisture: {
│   min: number
│   max: number
│   avg: number
│}
├── light_intensity: {
│   min: number
│   max: number
│   avg: number
│}
├── carbon_change_kg: number
├── trees_identified: number
├── device_status: string
└── created_at: Timestamp
```

---

### 7. `carbon_rates/` Collection  
Global reference data for carbon calculations (singleton pattern)
```
carbon_rates/{docId}
├── tree_carbon_absorption: map {
│   "Shorea robusta": {kg_per_month: 2.5, common_name: "Sal tree"},
│   "Pinus roxburghii": {kg_per_month: 1.8, common_name: "Chir Pine"},
│   "default": {kg_per_month: 2.0}
│}
├── vehicle_emissions: {
│   average_car_co2_per_mile: 0.41, // kg
│   average_car_mpg: 24.7
│}
├── credit_conversion: {
│   carbon_kg_per_credit: 1.0,
│   credit_usd_value: 15.00
│}
├── last_updated: Timestamp
└── source: string (e.g., "EPA 2024", "IPCC Guidelines")
```

---

### 8. `activity_logs/` Collection
Audit trail for security and debugging
```
activity_logs/{logId}
├── user_id: string
├── action: string ["data_received", "model_inference", "export", "delete", "auth_fail"]
├── device_id: string (if applicable)
├── status: string ["success", "error", "pending"]
├── error_message: string (if status == error)
├── timestamp: Timestamp
├── ip_address: string (optional)
└── metadata: map {}
```

---

## Security Rules (Firestore)

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users can read/write only their own profile
    match /users/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
    
    // Users can read their own devices
    match /devices/{deviceId} {
      allow read: if get(/databases/$(database)/documents/devices/$(deviceId)).data.user_id == request.auth.uid;
      allow write: if get(/databases/$(database)/documents/devices/$(deviceId)).data.user_id == request.auth.uid;
    }
    
    // Sensor readings - write only from authenticated devices
    match /sensor_readings/{deviceId}/{document=**} {
      allow read: if get(/databases/$(database)/documents/devices/$(deviceId)).data.user_id == request.auth.uid;
      allow write: if request.auth != null; // Cloud Function validates device
    }
    
    // Carbon calculations - read only
    match /carbon_credits/{userId}/{document=**} {
      allow read: if request.auth.uid == userId;
    }
    
    // Public reference data
    match /carbon_rates/{document=**} {
      allow read: if true;
      allow write: if false;
    }
  }
}
```

---

## Index Requirements

Run these in Firebase Console or deploy with `firestore.indexes.json`:

```json
{
  "indexes": [
    {
      "collectionGroup": "sensor_readings",
      "queryScope": "Collection",
      "fields": [
        {"fieldPath": "device_id", "order": "ASCENDING"},
        {"fieldPath": "timestamp", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "sensor_readings",
      "queryScope": "Collection",
      "fields": [
        {"fieldPath": "user_id", "order": "ASCENDING"},
        {"fieldPath": "timestamp", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "daily_summaries",
      "queryScope": "Collection",
      "fields": [
        {"fieldPath": "device_id", "order": "ASCENDING"},
        {"fieldPath": "date_key", "order": "DESCENDING"}
      ]
    }
  ]
}
```

---

## Data Flow Example

```
Arduino Sensor → POST /receiveSensorData
                    ↓
         Cloud Function validates
                    ↓
         Writes to sensor_readings/{deviceId}/
                    ↓
         Triggers daily aggregation
                    ↓
         Updates daily_summaries
                    ↓
         Monthly cron recalculates carbon_credits
                    ↓
         Frontend reads from daily_summaries & carbon_credits
```

---

## Initialization Script

Run once to set up reference data:

```python
# From CLI: python functions/init_firestore.py
import firebase_admin
from firebase_admin import firestore

db = firestore.client()

# Initialize carbon_rates
db.collection("carbon_rates").document("default").set({
    "tree_carbon_absorption": {
        "Shorea robusta": {"kg_per_month": 2.5, "common_name": "Sal tree"},
        "Pinus roxburghii": {"kg_per_month": 1.8, "common_name": "Chir Pine"},
        "default": {"kg_per_month": 2.0}
    },
    "vehicle_emissions": {
        "average_car_co2_per_mile": 0.41,
        "average_car_mpg": 24.7
    },
    "credit_conversion": {
        "carbon_kg_per_credit": 1.0,
        "credit_usd_value": 15.00
    },
    "last_updated": firestore.SERVER_TIMESTAMP,
    "source": "EPA 2024, IPCC Guidelines"
})

print("Firestore initialized!")
```
