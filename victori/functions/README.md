# HCCMS Functions Backend - Complete Documentation Index

Welcome to the HCCMS Backend implementation! All Cloud Functions, database schemas, and deployment guides are in this directory.

## 📚 Documentation Map

### 🚀 Getting Started (Start Here!)
1. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 5-minute overview of what's implemented
2. **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Step-by-step Firebase setup and deployment
3. **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API endpoint specifications

### 🤖 ML Model Deployment (Alternative Approach)
4. **[INFERENCE_SERVER_DEPLOYMENT.md](INFERENCE_SERVER_DEPLOYMENT.md)** - Flask server for free-tier tree identification
   - Deploy to Railway, Render, or Replit (no Firebase Blaze plan required)
   - Perfect for tree species classification via VGG16 model
   - Complete with API docs, integration guide, and troubleshooting

### 📋 Technical Reference
5. **[firestore_schema.md](firestore_schema.md)** - Database structure and collections
6. **[main.py](main.py)** - Cloud Functions source code (4 HTTP endpoints)
7. **[inference_server.py](inference_server.py)** - Flask ML inference server (alternative deployment)
8. **[init_firestore.py](init_firestore.py)** - Firestore initialization script
9. **[requirements.txt](requirements.txt)** - Python dependencies for Cloud Functions
10. **[requirements_inference.txt](requirements_inference.txt)** - Python dependencies for Flask server

---

## 🎯 What You Get

### ✅ Ready-to-Deploy Cloud Functions
Your backend consists of 4 production-ready HTTP functions:

```
receiveSensorData()        →  Accept sensor reading from Arduino
  ├─ Validates 8 sensor fields
  ├─ Authenticates device via API key
  ├─ Stores in Firestore sensor_readings
  └─ Updates device heartbeat

calculateDailySummary()    →  Aggregate daily sensor data
  ├─ Queries readings for specific date
  ├─ Calculates temp/humidity/moisture/light stats
  ├─ Computes daily carbon contribution
  └─ Stores in Firestore daily_summaries

getDeviceSummary()         →  Retrieve recent summaries
  ├─ Query parameter: device_id (required)
  ├─ Query parameter: days (optional, default 7)
  └─ Returns last N days of aggregated data

health_check()             →  Service status
  ├─ Returns service name and timestamp
  └─ Useful for monitoring and alerting
```

### ✅ Complete Firestore Schema
8 collections with security rules, indexes, and data models:

- `users/` - User account information
- `devices/` - Hardware device registry
- `sensor_readings/` - Raw sensor data (with sub-collections by device)
- `daily_summaries/` - Daily aggregated metrics
- `tree_identifications/` - ML model results
- `carbon_credits/` - Monthly carbon calculations
- `carbon_rates/` - Reference data (trees, emissions, credits)
- `activity_logs/` - Audit trail

### ✅ Production Features
- Data validation with Pydantic
- Device authentication
- CORS headers for frontend
- Error handling & logging
- Activity logging for audits
- Carbon calculation logic
- Firestore security rules

---

## 🚀 Quick Start

### If you have a Firebase project:

```bash
# 1. Make sure you're in the victori/functions directory
cd victori/functions

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Log in to Firebase
firebase login

# 4. Deploy Cloud Functions
firebase deploy --only functions

# 5. Register a test device in Firebase Console:
#    - Collection: devices
#    - Document ID: device_001
#    - Fields: {user_id: "user_123", api_key: "secret", status: "active"}

# 6. Test the API
curl -X POST "https://us-central1-YOUR_PROJECT.cloudfunctions.net/receiveSensorData" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"device_001","api_key":"secret","temperature":25.0,"humidity":60.0,"soil_moisture":70.0,"light_intensity":80.0}'
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed setup instructions.

---

## 📖 How to Read This Documentation

### Scenario 1: "I'm new to this project"
→ Start with [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### Scenario 2: "I need to set up Firebase and deploy"
→ Follow [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) from top to bottom

### Scenario 3: "How do I call the API from Arduino?"
→ Read [API_DOCUMENTATION.md](API_DOCUMENTATION.md) section on cURL examples, then scroll to "Integration Example"

### Scenario 4: "What's the Firestore structure?"
→ Check [firestore_schema.md](firestore_schema.md)

### Scenario 5: "I want to understand the code"
→ Review [main.py](main.py) with inline comments explaining each function

### Scenario 6: "Something's not working"
→ See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) "Troubleshooting" section

---

## 🔑 Key Concepts

### API Authentication
- Each device must be registered in Firestore
- Device provides: `device_id` + `api_key` with each request
- Cloud Function validates against Firestore database

### Data Flow
```
Arduino/ESP32 
   ↓ (HTTPS POST)
receiveSensorData()
   ↓ (validate + store)
Firestore: sensor_readings/{deviceId}/readings/{timestamp}
   ↓ (daily aggregation)
calculateDailySummary()
   ↓ (store aggregates)
Firestore: daily_summaries/{deviceId}/summaries/{date}
   ↓ (frontend queries)
getDeviceSummary()
   ↓ (JSON response)
Vue.js Dashboard
```

### Carbon Calculations
- Each reading includes environmental data (temperature, humidity, soil moisture)
- Daily summary calculates estimated CO2 absorbed based on:
  - Tree species carbon absorption rate
  - Soil moisture (tree health)
  - Temperature (photosynthesis efficiency)
- Results stored in carbon_credits collection for monthly summaries

---

## ⚙️ File Descriptions

### main.py
**Source code for all Cloud Functions**
- 4 decorated HTTP functions
- Uses firebase_admin SDK for Firestore access
- Pydantic models for request validation
- Error handling and logging
- ~380 lines of code with documentation

**Key Functions:**
```python
@https_fn.on_request(max_instances=20)
def receive_sensor_data(req)  # ← Most important, called by Arduino

@https_fn.on_request()
def calculate_daily_summary(req)

@https_fn.on_request()
def get_device_summary(req)

@https_fn.on_request()
def health_check(req)
```

### init_firestore.py
**One-time setup script**
- Populates carbon_rates collection with tree species data
- Sets up environmental factors
- Configures credit conversion rates

**Usage:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/serviceAccountKey.json"
python init_firestore.py
```

### firestore_schema.md
**Complete database schema documentation**
- 8 collections with field definitions
- Sample documents and data types
- Security rules for access control
- Index recommendations
- Data flow examples

### inference_server.py
**Flask REST API for VGG16 tree identification (Free-tier alternative)**
- Lightweight Python Flask application
- VGG16 deep learning model for 2-class tree classification
- Supports both file upload and image URL inference
- CORS enabled for cross-origin frontend requests
- 3 endpoints: /health, /classes, /identify

**Key Functions:**
```python
@app.route('/identify', methods=['POST'])
def identify_tree()  # ← Tree classification endpoint

@app.route('/health', methods=['GET'])
def health_check()  # ← Service health status

@app.route('/classes', methods=['GET'])
def get_classes()  # ← List supported tree classes
```

**Why This Over Cloud Functions?**
- Firebase Cloud Functions require Blaze (pay-as-you-go) plan
- This Flask server runs on free-tier services (Railway, Render, Replit)
- Same ML model (VGG16), different deployment strategy
- Can be deployed alongside Firebase for hybrid architecture

### INFERENCE_SERVER_DEPLOYMENT.md
**Complete deployment guide for Flask inference server**
- Local development setup
- API endpoint documentation with cURL examples
- 4 deployment options (Railway, Render, Replit, Ngrok)
- Firebase integration instructions
- Performance benchmarks
- Troubleshooting guide
- Production scaling recommendations

**Supported Platforms:**
- Railway.app (recommended, $5/month free tier)
- Render.com (free tier with 15-min sleep)
- Replit.com (instant deployment, auto URL)
- Local with Ngrok (development/testing)
- AWS Lambda, Google Cloud Run (advanced)

### API_DOCUMENTATION.md
**Full API reference for developers**
- 4 endpoints fully documented
- Request/response examples
- Field specifications and ranges
- Error codes and handlers
- cURL examples for testing
- Arduino integration example

### DEPLOYMENT_GUIDE.md
**Step-by-step deployment walkthrough**
- Firebase project setup (5 steps)
- Python environment configuration
- Local emulator testing
- Device registration methods
- Production deployment
- Monitoring and troubleshooting

### QUICK_REFERENCE.md
**One-page quick lookup guide**
- What's implemented (checklist)
- Quick start (5 minutes)
- Pre-deployment checklist
- API endpoints table
- Sample data flow diagram
- Common troubleshooting answers

---

## 🔍 Important File Locations

```
d:\betty\impact\
├── victori/
│   ├── functions/              ← YOU ARE HERE
│   │   ├── main.py            ← Cloud Functions code
│   │   ├── requirements.txt    ← Python dependencies
│   │   ├── init_firestore.py   ← Setup utility
│   │   ├── firebase.json       ← Firebase config
│   │   ├── serviceAccountKey.json  ← [CREATE THIS]
│   │   ├── firestore_schema.md    ← Database schema
│   │   ├── API_DOCUMENTATION.md   ← API specs
│   │   ├── DEPLOYMENT_GUIDE.md    ← Setup steps
│   │   ├── QUICK_REFERENCE.md     ← Quick lookup
│   │   └── README.md              ← You are reading this
│   │
│   ├── arduino/
│   │   └── plant_monitor.ino   ← [TODO] Add WiFi + API integration
│   │
│   ├── src/                    ← Vue.js frontend
│   │   ├── App.vue            ← [TODO] Dashboard integration
│   │   ├── firebase.ts
│   │   └── components/
│   │
│   └── BarkVisionAI-main/
│       └── src/
│           ├── train.py       ← ML model training
│           ├── test.py        ← [TODO] Connect to Cloud Functions
│           └── ...
│
└── HCCMS_PROJECT_GUIDE.md     ← Project overview
```

---

## ✨ Features & Status

### ✅ Completed (Backend Ready)
- [x] Cloud Functions implementation (4 endpoints)
- [x] Firestore schema design (8 collections)
- [x] Data validation (Pydantic models)
- [x] Device authentication (API key)
- [x] Carbon calculation logic
- [x] Error handling & logging
- [x] Activity audit trail
- [x] Complete documentation
- [x] Deployment guide
- [x] API reference

### ⏳ Next Phase (Arduino Integration)
- [ ] Arduino WiFi configuration
- [ ] HTTPS POST to Cloud Functions
- [ ] Sensor calibration
- [ ] Error recovery

### ⏳ Phase 3 (Frontend Integration)
- [ ] Vue.js dashboard
- [ ] Firestore real-time listeners
- [ ] User authentication
- [ ] Data visualization charts

### ⏳ Phase 4 (ML Integration)
- [ ] Tree identification endpoint
- [ ] Carbon credit calculation
- [ ] Monthly reporting

---

## 💡 Pro Tips

1. **Start Local:** Use Firebase emulator before deploying to production
   ```bash
   firebase emulators:start --only functions,firestore
   ```

2. **Monitor Logs:** Keep a terminal open with live logs during testing
   ```bash
   firebase functions:log --tail
   ```

3. **Test Incrementally:** Test each endpoint separately before integration
   ```bash
   # Test health check (simplest)
   curl "http://localhost:5001/your-project/us-central1/health_check"
   
   # Then test receive_sensor_data
   # Then test calculate_daily_summary
   ```

4. **Database Cost:** Monitor Firestore usage in Firebase Console
   - Reads are cheaper than writes
   - Batch sensor data (don't send every second)

5. **Versioning:** Always backup your Firestore before major changes
   - Use Firebase Console → Backups menu

---

## 🆘 Getting Help

### Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| Can't deploy functions | Check Firebase CLI: `firebase --version` |
| Device auth fails | Verify device in Firestore with correct api_key |
| Firestore writes fail | Check security rules are deployed: `firebase deploy --only firestore:rules` |
| Emulator won't start | Kill process on port 5001: `lsof -i :5001 \| kill -9` |
| Can't find Python modules | Activate venv: `source venv/bin/activate` (or .bat on Windows) |

### Debug Workflow
```bash
# 1. Check if functions deployed
firebase functions:list

# 2. View real-time logs
firebase functions:log --tail

# 3. Test with curl
curl "http://localhost:5001/project-id/us-central1/health_check"

# 4. Check Firestore data
firebase firestore:list

# 5. Verify security rules
firebase firestore:describe-rules
```

---

## 📞 Next Steps

1. **Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Full setup instructions
2. **Set up your Firebase project** - Create/configure Firestore
3. **Deploy Cloud Functions** - `firebase deploy --only functions`
4. **Register a test device** - Add to Firestore before sending data
5. **Test API endpoints** - Use cURL or Postman
6. **Connect Arduino** - Add WiFi + Cloud Function calls
7. **Build Vue Dashboard** - Create frontend to visualize data

---

## 📄 Document Links

- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Get oriented fast
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Setup & deploy
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API specs
- [firestore_schema.md](firestore_schema.md) - Database design
- [main.py](main.py) - Source code

---

**Backend Status:** ✅ **Production Ready for Deployment**  
**Last Updated:** February 5, 2026  
**Next Focus:** Arduino Integration + Vue.js Dashboard
