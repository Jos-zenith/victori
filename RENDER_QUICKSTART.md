# Render Deployment - Quick Start

## 🚀 Deploy to Render.com in 10 Minutes

### What's Included

✅ **render.yaml** - Infrastructure-as-code configuration  
✅ **Auto-deploy** - Push to GitHub triggers deployment  
✅ **Free tier** - 750 hours/month, no credit card required  
✅ **Health checks** - Automatic monitoring  
✅ **Environment variables** - Secure configuration  

---

## Quick Deploy

### Step 1: Push to GitHub
```bash
git add render.yaml
git commit -m "Add Render configuration"
git push origin main
```

### Step 2: Deploy Blueprint
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Blueprint"**
3. Connect **Jos-zenith/victori** repository
4. Click **"Apply"**

### Step 3: Get Your URL
After deployment completes (~10 min):
```
https://victori-inference-server.onrender.com
```

### Step 4: Test
```bash
curl https://victori-inference-server.onrender.com/health
# Response: {"status": "ok"}
```

---

## Configuration Details

### render.yaml Structure
```yaml
services:
  - type: web
    name: victori-inference-server
    runtime: python
    plan: free
    buildCommand: pip install -r victori/functions/requirements_inference.txt
    startCommand: python victori/functions/inference_server.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 5000
    healthCheckPath: /health
    autoDeploy: true
```

### What This Does
- **Installs** Python dependencies from requirements
- **Starts** Flask ML inference server
- **Monitors** health via `/health` endpoint
- **Auto-deploys** on every git push to main

---

## Important: Cold Starts

⚠️ **Render free tier spins down after 15 minutes of inactivity**

**First request after idle:** 30-60 seconds  
**Subsequent requests:** <1 second

### Solution: Keep Warm with UptimeRobot

1. Sign up at https://uptimerobot.com (free)
2. Create HTTP monitor:
   - URL: `https://victori-inference-server.onrender.com/health`
   - Interval: 5 minutes
   - Method: GET

This pings your service every 5 minutes, preventing cold starts.

---

## Update Frontend

After deploying, update your Next.js app:

```typescript
// app/api/identify-tree/route.ts
const INFERENCE_SERVER_URL = 
  process.env.INFERENCE_SERVER_URL || 
  'https://victori-inference-server.onrender.com';
```

For Vercel deployment:
```bash
vercel env add INFERENCE_SERVER_URL
# Enter: https://victori-inference-server.onrender.com
```

---

## Troubleshooting

### "Build failed"
Check build logs in Render dashboard for missing dependencies.

### "Model not found"
Ensure `victori/best_resnet50.pth` exists in repository:
```bash
git lfs track "*.pth"
git add victori/best_resnet50.pth
git commit -m "Add model file"
git push
```

### "Slow first request"
Expected behavior. Use UptimeRobot (see above) to keep service warm.

---

## Cost

**Free Tier:**
- 750 hours/month (always on)
- 100 GB bandwidth/month
- Cold starts after 15 min inactivity
- **$0/month**

**Starter Tier ($7/month):**
- No cold starts
- 500 GB bandwidth
- Better performance

---

## Complete Documentation

📖 **[RENDER_DEPLOYMENT.md](victori/functions/RENDER_DEPLOYMENT.md)** - Full deployment guide  
📊 **[DEPLOYMENT_COMPARISON.md](victori/functions/DEPLOYMENT_COMPARISON.md)** - Compare platforms  
🔧 **[inference_server.py](victori/functions/inference_server.py)** - Server source code  

---

## Next Steps

1. ✅ Deploy using steps above
2. ✅ Setup UptimeRobot to prevent cold starts
3. ✅ Update frontend with Render URL
4. ✅ Test tree identification API

**Need help?** See [RENDER_DEPLOYMENT.md](victori/functions/RENDER_DEPLOYMENT.md) for detailed troubleshooting!
