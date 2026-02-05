# Household Carbon Credit Monitoring System (HCCMS)
## Project Organization & Setup Guide

---

## 🏗️ PROJECT ARCHITECTURE OVERVIEW

```
HCCMS System
├── Hardware Layer (ESP32/Arduino)
│   └── Plant Monitor with Sensors
│       ├── DHT11 (Temperature/Humidity)
│       ├── Soil Moisture Sensor
│       ├── Light Sensor (LDR)
│       └── OLED Display
│
├── ML/Analytics Layer (Python)
│   ├── BarkVisionAI (Tree Species Identification)
│   ├── Data Processing & Carbon Calculations
│   └── Model Training & Inference
│
├── Backend Layer (Firebase)
│   ├── Cloud Functions (Python)
│   ├── Firestore Database
│   ├── Authentication
│   └── Hosting
│
└── Frontend Layer (Vue 3 + TypeScript)
    ├── Dashboard UI
    ├── Real-time Data Visualization
    └── User Management
```

---

## 📁 CURRENT WORKSPACE STRUCTURE

```
victori/
├── 📱 Frontend (Vue 3 + Vite)
│   ├── src/
│   │   ├── App.vue (Main component)
│   │   ├── firebase.ts (Firebase config)
│   │   ├── main.ts (Entry point)
│   │   └── components/ (UI components)
│   ├── package.json (Dependencies)
│   ├── vite.config.ts (Build config)
│   └── tsconfig.json
│
├── 🐍 ML & Analytics
│   └── BarkVisionAI-main/BarkVisionAI-main/
│       ├── src/ (Training scripts)
│       │   ├── train.py (Model training)
│       │   ├── test.py (Testing)
│       │   ├── prepare_model.py
│       │   ├── data_loader.py
│       │   └── vit_base_model.ipynb
│       ├── preprocessing scripts/ (Data prep notebooks)
│       ├── metadata.csv (Dataset metadata)
│       ├── requirements.txt (Python dependencies)
│       └── config.ini
│
├── ⚙️ Hardware
│   └── arduino/
│       └── plant_monitor/
│           └── plant_monitor.ino (Sensor reading & OLED display)
│
├── 🔥 Firebase Backend
│   ├── functions/
│   │   ├── main.py (Cloud Functions)
│   │   └── requirements.txt
│   ├── firebase.json (Deploy config)
│   ├── firestore.rules
│   └── firestore.indexes.json
│
└── 📊 Root Files
    ├── README.md (Main project docs)
    ├── package.json (Frontend deps)
    └── firebase.json (Firebase config)
```

---

## 🚀 SETUP & DEVELOPMENT WORKFLOW

### **Phase 1: Environment Setup**

#### 1.1 Frontend Setup (Vue.js + Vite)
```bash
cd victori
npm install
npm run dev              # Start dev server (typically http://localhost:5173)
```

#### 1.2 Python ML/Backend Environment
```bash
# Create virtual environment for Python projects
python -m venv venv
venv\Scripts\activate    # On Windows

# Install ML dependencies
cd BarkVisionAI-main/BarkVisionAI-main
pip install -r requirements.txt

# Install Firebase Functions dependencies
cd ../../functions
pip install -r requirements.txt
```

#### 1.3 Arduino/Hardware Setup
- Install Arduino IDE or PlatformIO
- Install required libraries:
  - Adafruit_GFX
  - Adafruit_SSD1306
  - DHT
  - Any WiFi/BLE library for ESP32 communication

---

### **Phase 2: Component Integration**

#### **Flow: Hardware → Backend → Frontend**

```
Arduino/ESP32 (Collects sensor data)
    ↓
    → Firebase Cloud Functions (Python) [Processes data, calls ML]
    ↓
    → ML Model (BarkVisionAI) [Identifies species, calculates carbon]
    ↓
    → Firestore Database [Stores results]
    ↓
    → Vue.js Frontend [Displays dashboard]
```

---

## 🔧 NEXT STEPS (In Priority Order)

### **IMMEDIATE (Week 1)**
- [ ] Configure Firebase project credentials
- [ ] Set up Cloud Functions API & authentication
- [ ] Create Firestore database schema for sensor data
- [ ] Test Arduino sensor connectivity and data transmission to Firebase

### **SHORT TERM (Week 2-3)**
- [ ] Implement Cloud Functions to receive Arduino data
- [ ] Deploy Python ML model inference to Firebase
- [ ] Create basic Vue.js dashboard to display real-time sensor data
- [ ] Implement carbon calculation logic

### **MEDIUM TERM (Week 4-5)**
- [ ] Integrate BarkVisionAI model for tree species identification
- [ ] Add historical data analysis and reporting
- [ ] Implement user authentication and multi-device support
- [ ] Add data export/analytics features

### **LONG TERM**
- [ ] Optimize ML model for edge devices (TensorFlow Lite on ESP32)
- [ ] Add predictive analytics
- [ ] Create mobile app wrapper
- [ ] Deploy to production Firebase hosting

---

## 📋 KEY FILES TO UPDATE/CREATE

### **Firebase Configuration**
- [ ] `victori/firebase.json` - Update with your Firebase project details
- [ ] `victori/functions/main.py` - Implement Cloud Functions for data processing
- [ ] `victori/src/firebase.ts` - Verify Firebase initialization

### **Arduino Configuration**
- [ ] `arduino/plant_monitor/plant_monitor.ino` - Add WiFi/Firebase connectivity
- [ ] Configure ESP32 WiFi credentials and Firebase server details

### **Frontend** 
- [ ] `src/components/Dashboard.vue` - Create dashboard for real-time data
- [ ] `src/components/DeviceManager.vue` - Manage multiple devices
- [ ] ``src/api/firebaseServices.ts` - Create Firestore query functions

### **Python Backend**
- [ ] `functions/carbon_calculator.py` - Carbon metrics calculation
- [ ] `functions/ml_inference.py` - Integrate BarkVisionAI model
- [ ] Update `functions/requirements.txt` with necessary packages

---

## 🔌 DATA SCHEMA (Firestore Example)

```
firestore/
├── devices/
│   └── {deviceId}
│       ├── name: string
│       ├── location: GeoPoint
│       └── status: string
│
├── sensor_readings/
│   └── {deviceId}/{timestamp}
│       ├── temperature: number
│       ├── humidity: number
│       ├── soil_moisture: number
│       ├── light_intensity: number
│       └── timestamp: Timestamp
│
├── tree_identification/
│   └── {deviceId}/{treeId}
│       ├── species: string
│       ├── confidence: number
│       ├── image_url: string
│       └── identified_at: Timestamp
│
└── carbon_credits/
    └── {deviceId}/{month}
        ├── carbon_absorbed: number
        ├── vehicle_emissions_offset: number
        └── credits_earned: number
```

---

## 🛠️ ESSENTIAL COMMANDS

```bash
# Frontend
npm run build             # Build for production
npm run dev              # Development server

# Firebase
firebase deploy          # Deploy Cloud Functions & configs
firebase serve           # Local testing
firebase login          # Authenticate with Firebase

# Python
python -m pip install --upgrade pip
pip install -r requirements.txt

# Arduino
# Use Arduino IDE or PlatformIO CLI
```

---

## ⚠️ CURRENT ISSUES IDENTIFIED

1. **BarkVisionAI Purpose Mismatch**: The current dataset is for tree species identification from bark, not carbon monitoring. Clarify if you need:
   - Tree species→carbon absorption rate mapping
   - Or separate carbon monitoring approach

2. **Firebase Cloud Functions Not Implemented**: `functions/main.py` is mostly commented out

3. **Arduino WiFi/Firebase Integration Missing**: Need to add connectivity to send data to Firebase

4. **Frontend Not Connected to Backend**: No Firestore queries or real-time updates implemented yet

5. **ML Model Deployment**: Need to implement inference pipeline in Cloud Functions

---

## 📞 TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Firebase auth errors | Check `google-services.json` & Firebase rules |
| Arduino WiFi connection fails | Verify ESP32 WiFi library & credentials |
| Python import errors | Ensure virtual environment activated |
| Frontend can't reach Firebase | Check Firebase initialization in `src/firebase.ts` |

---

## 📚 DOCUMENTATION REFERENCES

- [Firebase Python SDK](https://firebase.google.com/docs/functions/setup/deploy/python)
- [Vue 3 Guide](https://vuejs.org/guide/introduction.html)
- [Arduino ESP32 Reference](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
