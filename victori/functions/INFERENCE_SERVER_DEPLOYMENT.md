# Flask Inference Server Deployment Guide

This Flask server provides a lightweight, free-tier compatible alternative to Firebase Cloud Functions for VGG16 tree identification.

## Quick Start (Local Development)

### 1. Install Dependencies
```bash
cd victori/functions
pip install -r requirements_inference.txt
```

### 2. Prepare Model
Ensure `best_resnet50.pth` exists in the functions directory (already present).

### 3. Run Server Locally
```bash
python inference_server.py
```

Server will start at `http://localhost:5000`

## API Endpoints

### Health Check
```bash
curl http://localhost:5000/health
```
Response: `{"status": "ok"}`

### List Classes
```bash
curl http://localhost:5000/classes
```
Response:
```json
{
  "classes": ["Coconut Tree", "Mango Tree"],
  "num_classes": 2
}
```

### Identify Tree (Upload Image)
```bash
curl -X POST -F "file=@image.jpg" http://localhost:5000/identify
```

Response:
```json
{
  "prediction": "Coconut Tree",
  "confidence": 0.98,
  "class_id": 0,
  "processing_time": 0.123
}
```

### Identify Tree (Image URL)
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}' \
  http://localhost:5000/identify
```

## Deployment Options

### Option 1: Railway.app (Recommended)

**Advantages:** Free tier $5/month, automatic deployments, simple setup

1. **Create Railway Account**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Connect GitHub Repository**
   - Create a GitHub repo with project code
   - Connect to Railway

3. **Create requirements.txt** (already done as `requirements_inference.txt`)

4. **Set Environment Variables in Railway**
   - `FLASK_ENV`: `production`
   - `PORT`: 5000

5. **Deploy**
   ```bash
   git push origin main
   ```
   Railway automatically deploys on push

6. **Get Public URL**
   - Railway provides `https://yourapp.railway.app`
   - Use this URL in your Firebase functions

**Firebase Integration:**
```python
# In functions/main.py identify_tree_species()
response = requests.post(
    'https://yourapp.railway.app/identify',
    json={'image_url': image_url}
)
```

---

### Option 2: Render.com

**Advantages:** Free tier, auto-deploys from GitHub

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Connect GitHub repo
   - Set Build Command: `pip install -r requirements_inference.txt`
   - Set Start Command: `python inference_server.py`

3. **Environment Variables**
   - `FLASK_ENV`: `production`

4. **Deploy**
   - Render auto-deploys on GitHub push
   - Get URL: `https://yourapp.onrender.com`

**Note:** Free tier sleeps after 15 minutes of inactivity (5-10s delay on wake-up)

---

### Option 3: Replit

**Advantages:** Instant online IDE, free tier, no Git required

1. **Create Replit Account**
   - Go to https://replit.com
   - Sign up

2. **Create New Replit**
   - Import from GitHub OR paste files directly
   - Select Python as language

3. **Upload Files**
   - `inference_server.py`
   - `requirements_inference.txt`
   - `best_resnet50.pth`

4. **Run**
   - Click "Run" button
   - Replit provides public URL automatically

5. **Get Public URL**
   - Replit shows URL like `https://yourreplit.replit.dev`

---

### Option 4: Local with Port Forwarding (Ngrok)

For development/testing only:

1. **Install Ngrok**
   ```bash
   # MacOS
   brew install ngrok
   
   # Windows (download from ngrok.com)
   ```

2. **Run Server**
   ```bash
   python inference_server.py
   ```

3. **In Another Terminal**
   ```bash
   ngrok http 5000
   ```

4. **Get Public URL**
   ```
   https://xxxx-xx-xxx-xxx.ngrok.io
   ```

---

## Integrating with Firebase Functions

Update `functions/main.py`:

```python
import requests

INFERENCE_SERVER_URL = "https://yourapp.railway.app"  # Change to your deployed URL

def identify_tree_species(image_url: str) -> dict:
    """Identify tree species using Flask inference server"""
    try:
        response = requests.post(
            f"{INFERENCE_SERVER_URL}/identify",
            json={"image_url": image_url},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Inference error: {e}")
        return {"error": str(e)}
```

Deploy to Firebase:
```bash
firebase deploy --only functions
```

---

## Performance Notes

- **Model Loading:** ~2-3 seconds on first inference (cached after)
- **Inference Speed:** ~500ms per image
- **Memory Usage:** ~4GB RAM (model + Flask)
- **Concurrent Requests:** Handled via Flask threading (default 5 threads)

For production with high concurrency, consider Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 inference_server:app
```

---

## Monitoring & Logs

### Local Terminal
Logs appear in console where server is running

### Railway
- Dashboard shows real-time logs
- Monitor memory/CPU usage

### Render
- Logs tab in dashboard
- Free tier limited log retention

### Replit
- Console shows output in IDE

---

## Troubleshooting

**Issue:** "Port already in use"
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000    # Windows, then taskkill
```

**Issue:** "Model file not found"
- Ensure `best_resnet50.pth` uploaded to deployment
- Or upload to cloud storage (AWS S3, Firebase Storage) and download on startup

**Issue:** "Out of memory"
- Switch to CPU-only mode (modify inference_server.py: `device = torch.device('cpu')`)
- Memory will drop to ~1GB

**Issue:** Slow inference on free tier
- Normal for cold starts (first request after inactivity)
- Subsequent requests much faster

---

## Next Steps

1. Choose deployment platform
2. Upload files to platform
3. Get public URL
4. Update Firebase functions with URL
5. Test end-to-end with sample images

For production scale (>100 requests/day), consider:
- Upgrading Railway to paid tier ($10+/month)
- Using AWS Lambda + free tier (1M invocations/month)
- Google Cloud Run ($0.00001/GB-second, very cheap)
