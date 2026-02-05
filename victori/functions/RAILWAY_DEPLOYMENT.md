# Deploy Flask Inference Server to Railway

## ⚡ Quick Start (10 minutes)

### Prerequisites
- GitHub account
- Railway account (free at https://railway.app)

### Step 1: Create GitHub Repository

```bash
cd d:\betty\impact
git init
git add -A
git commit -m "Initial commit - HCCMS project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/victori.git
git push -u origin main
```

### Step 2: Deploy to Railway

1. **Go to https://railway.app**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your `victori` repository**
6. **Railway auto-detects it's a Python project**

### Step 3: Configure Environment Variables

In Railway dashboard:

1. Click "Variables" tab
2. Add these variables:
   ```
   FLASK_ENV=production
   ```

3. **Important:** If using Flask server with Cloud Functions, set:
   ```
   INFERENCE_SERVER_URL=https://<your-railway-domain>/
   ```
   (Railway generates this when deployed)

### Step 4: Configure Entry Point

Railway auto-detects `inference_server.py`. But verify:

1. Go to "Settings" tab
2. Find "Start Command"
3. Should be: `python inference_server.py`
4. If not, set it manually

### Step 5: Verify Deployment

```bash
# Once deployed, Railway shows your URL like:
# https://victori-production-xyz.railway.app

# Test health check
curl https://victori-production-xyz.railway.app/health

# Test classes endpoint
curl https://victori-production-xyz.railway.app/classes
```

---

## 🚀 Full Deployment Steps with Details

### A. Prepare Project

```bash
# From workspace root
cd d:\betty\impact\victori

# Create .gitignore if needed
# (already exists, but verify it has these)
echo "node_modules/" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "dist/" >> .gitignore

# Initialize git
git init
git add -A
git commit -m "HCCMS - Flask inference server ready for deployment"
```

### B. Push to GitHub

1. **Create new repo on GitHub:**
   - Go to https://github.com/new
   - Name it: `victori` or `hccms-flask`
   - Make it Public or Private
   - Click "Create repository"

2. **Push your code:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/victori.git
   git branch -M main
   git push -u origin main
   ```

### C. Deploy to Railway

1. **Go to Railway.app**
2. **Click "Start a New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Authorize Railway to access your GitHub**
5. **Select the `victori` repository**
6. **Railway automatically:**
   - Detects Python project
   - Creates Procfile or uses inference_server.py
   - Sets PORT environment variable
   - Builds and deploys

7. **Wait for deployment** (~3-5 minutes)
   - Green checkmark = Success
   - Activity log shows the URL

---

## 🔗 Integrate with Cloud Functions

Once Flask is deployed, update Cloud Functions to use it:

### Update main.py

```python
# At deploy time, set environment variable:
INFERENCE_SERVER_URL = "https://victori-production-xyz.railway.app"

# This will be used by identify_tree_species() function
```

### Deploy Cloud Functions

```bash
cd d:\betty\impact\victori
firebase deploy --only functions
```

---

## ✅ Verify Everything Works

### 1. Test Flask Health
```bash
curl -X GET https://YOUR-RAILWAY-URL/health
# Should return: {"status": "healthy", ...}
```

### 2. Test Flask Inference
```bash
curl -X POST https://YOUR-RAILWAY-URL/identify \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/tree.jpg"}'
```

### 3. Test Cloud Function Integration
```bash
curl -X POST https://YOUR-CLOUD-FUNCTION-URL/identifyTreeSpecies \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "URL_TO_TREE_IMAGE",
    "device_id": "test_device",
    "api_key": "test_key"
  }'
```

---

## 📊 Monitor Deployment

### Railway Dashboard
1. Click on your deployment
2. View logs in real-time
3. Monitor memory/CPU usage
4. Check build history

### Using Flask Logs
```bash
# On Railway, go to "Logs" tab
# You'll see:
# - Model loading status
# - Inference requests
# - Error messages
# - Performance metrics
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Deploy fails | Check build logs - might be Python version or dependency issue |
| Model not found | Ensure `best_resnet50.pth` is in git and pushed |
| 503 error | Cold start - Railway is initializing. Wait 30s and retry |
| Slow inference | Right - first request triggers model load (~3s) |
| Out of memory | Railway free tier has 512MB RAM. Model needs ~1GB |

### Common Fixes

**If model file not found:**
```bash
# Add to git
git add victori/functions/best_resnet50.pth
git commit -m "Add trained model"
git push
# Railway auto-redeploys
```

**If still failing:**
- Use GitHub releases to store model
- Or add to Firebase Storage and download on startup

---

## 💰 Cost Breakdown

| Service | Free Tier | Cost |
|---------|-----------|------|
| Railway | $5/month credit | $0-5 (~1-2 small apps) |
| Flask server | Included | $0 |
| Inference | Per request | $0 (included in Railway) |

---

## 📝 Environment Variables Reference

```bash
# For Flask server (inference_server.py)
FLASK_ENV=production    # or 'development'
PORT=5000              # Railway sets this (don't override)

# For Cloud Functions integration (main.py)
INFERENCE_SERVER_URL=https://your-railway-url
INFERENCE_ENABLED=true  # Enable/disable ML
```

---

## 🎯 Next: Update Cloud Functions

Once Flask is deployed at `https://your-url`, update the Cloud Function deployment:

1. **Update environment variable in Cloud Functions:**
   ```bash
   firebase functions:config:set \
     inference.server_url="https://your-railway-url"
   ```

2. **Or set it in .env.local:**
   ```
   INFERENCE_SERVER_URL=https://your-railway-url
   INFERENCE_ENABLED=true
   ```

3. **Deploy functions:**
   ```bash
   firebase deploy --only functions
   ```

---

## 🚀 Summary

✅ Flask server deployed to Railway  
✅ Public URL established  
✅ Cloud Functions configured to call Flask  
✅ ML inference ready for production  

**You now have a complete ML pipeline:**
- Image upload → Cloud Function
- Cloud Function calls Flask
- Flask identifies tree species
- Results stored in Firestore
