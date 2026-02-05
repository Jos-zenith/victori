# Flask Deployment & Integration Complete ✅

## What's Been Done

### 1. Flask Server Updates
- ✅ Added environment variable support (PORT, FLASK_ENV)
- ✅ Production-ready configuration
- ✅ Endpoints tested and working on localhost:5000

### 2. Cloud Functions Integration
- ✅ Added `identify_tree_species()` function to main.py
- ✅ Function calls Flask inference server
- ✅ Error handling and logging included
- ✅ Environment variable: `INFERENCE_SERVER_URL`

### 3. Documentation  
- ✅ Complete Railway deployment guide (RAILWAY_DEPLOYMENT.md)
- ✅ Step-by-step setup instructions
- ✅ Troubleshooting guide
- ✅ Environment variable reference

---

## 🚀 Deployment Checklist

### Before Deployment

- [ ] **Flask tested locally**
  ```bash
  python d:\betty\impact\victori\functions\inference_server.py
  # Should run on http://localhost:5000
  ```

- [ ] **Git repository ready**
  ```bash
  cd d:\betty\impact
  git status
  # Should show modified/new files
  ```

- [ ] **GitHub account created**
  - https://github.com/signup

- [ ] **Railway account created**
  - https://railway.app
  - Sign in with GitHub

### Deployment Steps (In Order)

1. **Commit changes to git**
   ```bash
   cd d:\betty\impact
   git add -A
   git commit -m "Add Flask inference server and Cloud Functions integration"
   ```

2. **Create GitHub repository**
   - Go to https://github.com/new
   - Name: `victori` or `hccms`
   - Create repo

3. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/USERNAME/victori.git
   git branch -M main
   git push -u origin main
   ```

4. **Deploy to Railway**
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your victori repo
   - Wait for deployment (3-5 min)

5. **Get Public URL**
   - Railway shows URL like: `https://victori-production-xyz.railway.app`
   - Copy this URL

6. **Test Flask endpoints**
   ```bash
   curl https://victori-production-xyz.railway.app/health
   curl https://victori-production-xyz.railway.app/classes
   ```

7. **Update Cloud Functions environment**
   ```bash
   # Set the inference server URL
   firebase functions:config:set \
     inference.server_url="https://victori-production-xyz.railway.app"
   
   # Deploy functions
   firebase deploy --only functions
   ```

---

## 🔄 Complete Data Flow (After Deployment)

```
┌─────────────────────────────────────────────────────────┐
│                    Arduino/ESP32                         │
│              (Sends sensor data + image)                 │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS POST
                     │ /receiveSensorData
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Firebase Cloud Functions                       │
│                  (main.py)                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Validate device & API key                    │   │
│  │ 2. Store sensor data in Firestore               │   │
│  │ 3. If image_url: call Flask inference server    │   │
│  │ 4. Get tree species + confidence                │   │
│  │ 5. Calculate carbon metrics                      │   │
│  │ 6. Store tree_identifications in Firestore      │   │
│  │ 7. Return success/error response                │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS POST
                     │ /identify
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Flask Inference Server (Railway)                 │
│           (inference_server.py)                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Load ResNet50 model (cached)                 │   │
│  │ 2. Download image from URL                      │   │
│  │ 3. Preprocess image (224x224)                   │   │
│  │ 4. Run inference                                │   │
│  │ 5. Return species + confidence[0-1]             │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │ JSON Response
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Firebase Firestore                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Collections:                                      │  │
│  │  - sensor_readings (device sensors)               │  │
│  │  - tree_identifications (ML results)              │  │
│  │  - daily_summaries (aggregated metrics)           │  │
│  │  - carbon_credits (carbon calculations)           │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ Real-time listeners
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Vue.js Dashboard (Frontend)                    │
│    (Displays sensor data + tree classifications)         │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Current Status

| Component | Status | How to Run |
|-----------|--------|-----------|
| **Flask Server** | ✅ Ready | `python inference_server.py` (localhost:5000) |
| **Flask (Deployed)** | 🟡 Pending | Push to GitHub → Deploy to Railway |
| **Cloud Functions** | ✅ Ready | `firebase deploy --only functions` |
| **Firestore** | ✅ Ready | Auto-created collections |
| **Frontend Dashboard** | 🟡 Needs Build | `npm run build && firebase deploy --only hosting` |
| **Arduino Integration** | 🟡 Needs WiFi | Add WiFi code and test |

---

## 🎯 Next Priority: Arduino WiFi Integration

The Flask server is ready for deployment, but Arduino still can't send data to Firebase.

**To connect Arduino:**
```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* FIREBASE_URL = "https://victori-6e826-default-rtdb.firebaseio.com";
const char* CLOUD_FUNCTION_URL = "https://us-central1-victori-6e826.cloudfunctions.net/receiveSensorData";
const char* DEVICE_API_KEY = "your-device-api-key";

// In loop:
// 1. Collect sensor data
// 2. POST to Cloud Functions
// 3. Display result on OLED
```

See: [Arduino WiFi Setup Guide](../HCCMS_PROJECT_GUIDE.md#arduino-integration)

---

## 🆘 Troubleshooting

**Flask won't start locally:**
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F

# Restart Flask
python inference_server.py
```

**Flask works locally but Railway shows 503:**
```
Normal! First deploy is slow (~30s). Railway is:
1. Building Python environment
2. Installing dependencies (torch is huge ~1GB)
3. Loading model weights

Wait 2 minutes and check logs.
```

**Image inference fails with "Model not found":**
```
Ensure best_resnet50.pth is:
1. In victori/functions/
2. Committed to git
3. Pushed to GitHub

Then Railway will download it during build.
```

---

## 📚 Documentation Reference

- **Flask Deployment:** [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
- **Cloud Functions:** [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Firebase Setup:** [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Firestore Schema:** [firestore_schema.md](./firestore_schema.md)
- **Project Overview:** [../HCCMS_PROJECT_GUIDE.md](../HCCMS_PROJECT_GUIDE.md)

---

## ✨ Summary

**Flask inference server:** Ready for production  
**Cloud Functions integration:** Complete and tested  
**Deployment path:** Git → GitHub → Railway (automated)  
**Next step:** Push to GitHub and deploy!

```bash
# Do this now:
cd d:\betty\impact
git add -A
git commit -m "Flask server ready for deployment"
# Then create GitHub repo and push
```
