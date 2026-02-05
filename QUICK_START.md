# HCCMS Quick Start Checklist

## ✅ PRE-SETUP CHECKLIST
- [ ] Firebase project created and activated
- [ ] Arduino IDE or PlatformIO installed
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Git configured on this machine

## 🔧 COMPONENT-BY-COMPONENT SETUP

### Arduino/ESP32 Setup
```
1. Open arduino/plant_monitor/plant_monitor.ino
2. Update ESP32 board settings in Arduino IDE
3. Install libraries listed in comments
4. Configure:
   - WiFi network name/password
   - Firebase host/auth token
5. Upload to ESP32
6. Test via OLED display
```

### Python Environment Setup
```
# From d:\betty\impact directory (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install ML dependencies
cd victori\BarkVisionAI-main\BarkVisionAI-main
pip install -r requirements.txt

# Install Firebase Functions dependencies  
cd ..\..\functions
pip install -r requirements.txt
```

### Firebase Setup
```
# Install Firebase CLI (if not already installed)
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase project (from victori directory)
firebase init

# Deploy
firebase deploy

# View logs
firebase functions:log
```

### Frontend Setup
```
cd victori
npm install
npm run dev
# Open http://localhost:5173 in browser
```

## 🔴 BLOCKING ISSUES TO RESOLVE NOW

1. **Firebase Configuration**
   - Obtain your `google-services.json` from Firebase Console
   - Update Firebase project ID in all config files
   - Enable Firestore & Cloud Functions API

2. **Arduino WiFi Module**
   - Verify ESP32 has WiFi capability (most do)
   - Update WiFi SSID/password in sketch
   - Obtain Firebase database URL

3. **Python Package Conflicts**
   - May need to resolve version conflicts in requirements.txt
   - Test imports: `python -c "import tensorflow; import firebase_admin"`

4. **Frontend-Backend Communication**
   - Implement real-time Firestore listeners in Vue
   - Set up proper CORS for Cloud Functions

## 📊 DATA FLOW VERIFICATION

After setup, test each link:
```
Arduino Sketch
  → Compiles & uploads? ✓
  
ESP32 Device
  → Connects to WiFi? ✓
  → Reads sensors correctly? ✓
  → Sends data to Firebase? ✓
  
Firebase Cloud Function
  → Receives data? ✓
  → Processes (ML model)? ✓
  → Stores in Firestore? ✓
  
Vue Frontend
  → Loads dashboard? ✓
  → Displays real-time data? ✓
  → User can interact? ✓
```

## 🎯 FOCUS AREAS THIS WEEK

**Priority 1**: Get Arduino → Firebase data pipeline working
**Priority 2**: Implement basic Cloud Function to receive & store data
**Priority 3**: Build simple Vue dashboard to display data
**Priority 4**: Add ML model inference to pipeline

---

**Questions to clarify with team:**
- Is BarkVisionAI model the right fit for carbon monitoring, or do you need a different model?
- Do you have Firebase credentials ready?
- What's the target deployment MVP scope?
