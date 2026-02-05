# HCCMS Cloud Functions - Complete Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Firebase Project Setup](#firebase-project-setup)
3. [Local Development](#local-development)
4. [Register Your First Device](#register-your-first-device)
5. [Deploy to Production](#deploy-to-production)
6. [Testing](#testing)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Prerequisites

### Required Software
```bash
# Node.js 14+
node --version

# Firebase CLI
npm install -g firebase-tools

# Python 3.8+
python --version

# Git
git --version
```

### Required Accounts
- Google account with Firebase access
- Firebase project created in Google Cloud Console

---

## Firebase Project Setup

### Step 1: Create Firebase Project
```bash
# Login to Firebase
firebase login

# List your projects
firebase projects:list

# Or create new project (via Google Cloud Console)
# https://console.firebase.google.com
```

### Step 2: Initialize Firestore
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Navigate to **Firestore Database**
4. Click **Create Database**
5. Choose **Start in production mode**
6. Select region (e.g., us-central1)
7. Click **Create**

### Step 3: Enable Required APIs
1. Go to Google Cloud Console → APIs & Services → Library
2. Search and enable:
   - Cloud Functions API
   - Cloud Build API
   - Cloud Logging API
   - Cloud Pub/Sub API

### Step 4: Set Up Service Account
```bash
# Get project ID
firebase use

# Create service account key
# 1. Go to Project Settings → Service Accounts
# 2. Click "Generate new private key"
# 3. Save as `victori/functions/serviceAccountKey.json`

# Or via CLI:
gcloud iam service-accounts keys create functions/serviceAccountKey.json \
  --iam-account=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
```

### Step 5: Update Firebase Config
Edit `victori/firebase.json`:
```json
{
  "projects": {
    "default": "your-project-id"
  },
  "functions": {
    "source": "functions",
    "runtime": "python39",
    "codebase": "hccms-python-functions"
  }
}
```

---

## Local Development

### Step 1: Setup Python Environment
```bash
# Navigate to functions directory
cd victori/functions

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Local Emulator
```bash
# Install emulator (from project root)
firebase emulators:install

# Start emulator
firebase emulators:start --only functions,firestore

# Output will show:
# ✔  functions: http://localhost:5001/your-project-id/us-central1/
# ✔  firestore: http://localhost:8080
```

### Step 3: Test Endpoints Locally
```bash
# In another terminal, test the health check
curl http://localhost:5001/your-project-id/us-central1/health_check

# Test sensor data endpoint
curl -X POST http://localhost:5001/your-project-id/us-central1/receiveSensorData \
  -H 'Content-Type: application/json' \
  -d '{
    "device_id": "test_device",
    "api_key": "test_api_key",
    "temperature": 25.0,
    "humidity": 60.0,
    "soil_moisture": 70.0,
    "light_intensity": 80.0,
    "battery": 100,
    "rssi": -50
  }'
```

### Step 4: View Emulator Data
- Firestore Emulator UI: http://localhost:4000

---

## Register Your First Device

### Option A: Via Firebase Console

1. Go to Firestore Database
2. Create collection **devices**
3. Create document with ID: `device_001`
4. Add these fields:
```
user_id: "user_123"
name: "Test Device"
device_type: "esp32"
api_key: "secret_test_key_12345"
status: "active"
battery_level: 100
timezone: "UTC"
created_at: (current timestamp)
updated_at: (current timestamp)
```

### Option B: Via Python Script

Create `register_device.py`:
```python
import firebase_admin
from firebase_admin import firestore
from datetime import datetime

firebase_admin.initialize_app()
db = firestore.client()

device_data = {
    "user_id": "user_123",
    "name": "Front Yard Monitor",
    "device_type": "esp32",
    "firmware_version": "1.0.0",
    "serial_number": "ESP32-001",
    "api_key": "secret_api_key_12345",
    "status": "active",
    "battery_level": 100,
    "timezone": "UTC",
    "sensors": {
        "temperature": True,
        "humidity": True,
        "soil_moisture": True,
        "light_intensity": True,
        "co2": False
    },
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

db.collection("devices").document("device_001").set(device_data)
print("✓ Device registered!")
```

Run it:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/serviceAccountKey.json"
python register_device.py
```

---

## Deploy to Production

### Step 1: Build & Test
```bash
# From project root
cd victori/functions

# Ensure all tests pass
python -m pytest (if you have tests)

# Or just verify imports
python -c "from main import receive_sensor_data; print('✓ Functions OK')"
```

### Step 2: Deploy Functions
```bash
# From project root
firebase deploy --only functions

# Output includes:
# Function URL (HTTP trigger):
# https://us-central1-your-project-id.cloudfunctions.net/receiveSensorData
```

### Step 3: Deploy Firestore Security Rules
```bash
# Update firestore.rules with your rules
# Then deploy:
firebase deploy --only firestore:rules
```

### Step 4: Initialize Reference Data
```bash
# Set environment variable (Windows PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS = "victori/functions/serviceAccountKey.json"

# Or Linux/Mac:
export GOOGLE_APPLICATION_CREDENTIALS="victori/functions/serviceAccountKey.json"

# Run initialization
python victori/functions/init_firestore.py
```

### Step 5: Verify Deployment
```bash
# Get function URLs
firebase functions:list
# Output:
# ✔  receive_sensor_data (HTTP)
# ✔  calculate_daily_summary (HTTP)
# ✔  get_device_summary (HTTP)
# ✔  health_check (HTTP)

# View logs
firebase functions:log
```

---

## Testing

### Manual Testing with cURL

#### Test 1: Health Check
```bash
curl "https://us-central1-your-project-id.cloudfunctions.net/health_check"
```

#### Test 2: Send Sensor Data
```bash
curl -X POST "https://us-central1-your-project-id.cloudfunctions.net/receiveSensorData" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device_001",
    "api_key": "secret_api_key_12345",
    "temperature": 25.5,
    "humidity": 65.0,
    "soil_moisture": 75.0,
    "light_intensity": 85.0,
    "battery": 95,
    "rssi": -45
  }'
```

#### Test 3: Calculate Daily Summary
```bash
curl -X POST "https://us-central1-your-project-id.cloudfunctions.net/calculateDailySummary" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device_001",
    "date": "2026-02-05"
  }'
```

#### Test 4: Get Device Summary
```bash
curl "https://us-central1-your-project-id.cloudfunctions.net/getDeviceSummary?device_id=device_001&days=7"
```

### Load Testing (Optional)
```bash
# Using Apache Bench
ab -n 100 -c 10 "https://us-central1-your-project-id.cloudfunctions.net/health_check"
```

---

## Monitoring & Troubleshooting

### View Real-Time Logs
```bash
firebase functions:log --tail
```

### Check Function Performance
1. Go to Firebase Console
2. Navigate to Functions
3. Check memory usage, execution time, error rate

### Common Issues

#### Issue: "Device not found" (401)
**Solution:** Ensure device is registered in Firestore `devices` collection
```bash
# Verify device exists:
firebase firestore:list devices/device_001
```

#### Issue: "Invalid API key" (401)
**Solution:** Check api_key matches exactly
```
# Device document must have:
api_key: "secret_api_key_12345"

# Request must have same value:
"api_key": "secret_api_key_12345"
```

#### Issue: "Device is not active" (401)
**Solution:** Update device status field
```bash
# In Firebase Console, set:
devices/device_001 → status: "active"
```

#### Issue: Validation errors (400)
**Solution:** Check field ranges:
- temperature: -50 to 60°C
- humidity: 0 to 100%
- soil_moisture: 0 to 100%
- light_intensity: 0 to 100%

#### Issue: Firestore write errors
**Solution:** Check security rules allow writes
```
# In firestore.rules:
match /sensor_readings/{deviceId}/{document=**} {
  allow write: if request.auth != null;
}
```

### Debug Mode
Enable debug logging in main.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Cost Optimization

### Firestore Billing
- **Reads:** ~$0.06 per 100K reads
- **Writes:** ~$0.18 per 100K writes
- **Deletes:** ~$0.02 per 100K deletes

### Cost Control Tips
1. **Batch sensor writes** - Send data every 10 minutes instead of continuous
2. **TTL on old data** - Auto-delete sensor readings older than 90 days
3. **Use indexes wisely** - Only index frequently queried fields
4. **Limit daily summaries** - Pre-aggregate data instead of querying raw readings

### Set TTL on sensor_readings (Premium Firestore)
```bash
# Enable TTL in Firebase Console:
# Firestore → Data → sensor_readings → Create Index
# Set TTL policy on "timestamp" field (90 days)
```

---

## Next Steps

After successful deployment:

1. **Configure Arduino/ESP32** - Add WiFi and API integration
2. **Build Frontend Dashboard** - Create Vue.js dashboard to display data
3. **Set Up Automated Jobs** - Add monthly carbon credit calculations
4. **Implement Authentication** - Add user login system
5. **Production Hardening** - Add rate limiting, encryption, backups

---

## Additional Resources

- [Firebase Cloud Functions Docs](https://firebase.google.com/docs/functions)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Python Firebase Admin SDK](https://firebase.google.com/docs/reference/admin)
- [Emulator Suite](https://firebase.google.com/docs/emulator-suite)

---

## Support & Issues

If you encounter problems:

1. Check logs: `firebase functions:log --tail`
2. Check Firestore console for data
3. Verify service account permissions
4. Review security rules
5. Check function memory/timeout settings

**Debug tip:** Add print statements and check logs in real-time with `--tail`
