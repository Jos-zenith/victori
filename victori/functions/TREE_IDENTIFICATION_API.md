# Tree Identification API - Usage Guide

## Overview
The `identify-tree-species` endpoint uses a pre-trained ResNet50 model (trained on BarkVisionAI dataset) to identify tree species from bark images and provide carbon absorption estimates.

**Model:** ResNet50 - BarkVisionAI  
**Accuracy:** 87.42%  
**Classes:** 13 tree species  
**Framework:** PyTorch

---

## Endpoint Details

### POST /identifyTreeSpecies

Identifies tree species from a bark image and stores the result in Firestore.

**URL:**
```
https://us-central1-{PROJECT_ID}.cloudfunctions.net/identifyTreeSpecies
```

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "device_id": "device_001",
    "image_url": "https://example.com/bark_image.jpg",
    "location": {
        "latitude": 31.5497,
        "longitude": 77.1703
    }
}
```

**Field Specifications:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `device_id` | string | ✓ | Unique device identifier (must exist in Firestore) |
| `image_url` | string | ✓ | URL or file path to bark image (JPEG/PNG) |
| `location` | object | ✗ | GPS coordinates of the tree |
| `location.latitude` | float | ✗ | Latitude (-90 to 90) |
| `location.longitude` | float | ✗ | Longitude (-180 to 180) |

**cURL Example:**
```bash
curl -X POST "https://us-central1-hccms-project.cloudfunctions.net/identifyTreeSpecies" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device_001",
    "image_url": "https://example.com/tree_bark.jpg",
    "location": {
      "latitude": 31.5497,
      "longitude": 77.1703
    }
  }'
```

---

## Success Response (201)

```json
{
    "success": true,
    "tree_id": "abc123def456",
    "species": "Shorea robusta",
    "confidence": 0.9234,
    "confidence_level": "very_high",
    "carbon_rate_kg_per_month": 2.5,
    "message": "Tree identified as Shorea robusta with 92.3% confidence"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether identification was successful |
| `tree_id` | string | Unique identifier for this tree identification record |
| `species` | string | Identified tree species name |
| `confidence` | float | Model confidence score (0-1) |
| `confidence_level` | string | Human-readable confidence: `very_high`, `high`, `medium`, `low`, `very_low` |
| `carbon_rate_kg_per_month` | float | Estimated monthly CO2 absorption (kg) |
| `message` | string | Descriptive summary |

---

## Supported Tree Species

The model can identify 13 tree species from the BarkVisionAI dataset:

| Species | Scientific Name | Carbon Rate (kg/month) |
|---------|-----------------|----------------------|
| Sal tree | *Shorea robusta* | 2.5 |
| Chir Pine | *Pinus roxburghii* | 1.8 |
| Deodar Cedar | *Cedrus deodara* | 2.3 |
| Charoli | *Buchanania lanzan* | 1.9 |
| Mahua tree | *Madhuca longifolia* | 2.1 |
| Mango | *Mangifera sylvatica* | 2.0 |
| Indian gooseberry | *Phyllanthus emblica* | 1.8 |
| Oak | *Quercus leucotrichophora* | 2.4 |
| Rhododendron | *Rhododendron arboreum* | 2.0 |
| Acacia | *Senegalia catechu* | 1.7 |
| Horse chestnut | *Aesculus indica* | 2.2 |
| Yew | *Taxus baccata* | 2.1 |
| Blue gum | *Eucalyptus globulus* | 2.8 |

---

## Error Responses

### 400 Bad Request - Missing Fields
```json
{
    "error": "device_id and image_url are required"
}
```

### 400 Bad Request - Image Processing Failed
```json
{
    "error": "Failed to load image from URL"
}
```

### 404 Not Found - Device Not Registered
```json
{
    "error": "Device not found"
}
```

### 500 Server Error
```json
{
    "error": "Server error: [error details]"
}
```

---

## Confidence Levels

The model returns a confidence score (0-1):

| Confidence | Level | Interpretation |
|------------|-------|-----------------|
| ≥ 0.9 | **very_high** | Highly reliable identification |
| 0.7 - 0.9 | **high** | Reliable, good match |
| 0.5 - 0.7 | **medium** | Possible match, review recommended |
| 0.3 - 0.5 | **low** | Uncertain, may need manual verification |
| < 0.3 | **very_low** | Not reliable, highly uncertain |

**Recommendation:** Only automatically accept identifications with confidence ≥ 0.7

---

## Arduino/ESP32 Integration

Send bark image from your camera to this endpoint:

```cpp
// Arduino example
#include <HTTPClient.h>
#include <ArduinoJson.h>

void identifyTreeAndCalculateCarbon() {
    WiFiClient client;
    HTTPClient http;
    
    String url = "https://us-central1-PROJECT_ID.cloudfunctions.net/identifyTreeSpecies";
    http.begin(client, url);
    http.addHeader("Content-Type", "application/json");
    
    DynamicJsonDocument doc(500);
    doc["device_id"] = "device_001";
    doc["image_url"] = "https://your-storage.com/image_20260205_143000.jpg";
    doc["location"]["latitude"] = gpsLatitude;
    doc["location"]["longitude"] = gpsLongitude;
    
    String payload;
    serializeJson(doc, payload);
    
    int httpCode = http.POST(payload);
    
    if (httpCode == 201) {
        DynamicJsonDocument response(500);
        deserializeJson(response, http.getString());
        
        String species = response["species"];
        float carbonRate = response["carbon_rate_kg_per_month"];
        
        // Store in Firestore or display on OLED
        Serial.print("Tree: ");
        Serial.print(species);
        Serial.print(" | Carbon: ");
        Serial.print(carbonRate);
        Serial.println(" kg/month");
    }
    
    http.end();
}
```

---

## Data Storage

Results are automatically stored in Firestore:

**Collection:** `tree_identifications`

**Document Fields:**
```json
{
    "device_id": "device_001",
    "user_id": "user_123",
    "species": "Shorea robusta",
    "confidence": 0.9234,
    "confidence_level": "very_high",
    "class_id": 11,
    "carbon_rate_kg_per_month": 2.5,
    "image_url": "https://example.com/image.jpg",
    "location": {
        "latitude": 31.5497,
        "longitude": 77.1703
    },
    "identified_at": Timestamp,
    "model_version": "ResNet50-BarkVisionAI",
    "processing_time_ms": 1250
}
```

---

## Performance

- **Model Load Time:** ~2-5 seconds (first call)
- **Inference Time:** ~500-1000ms per image
- **Memory Usage:** ~400MB (PyTorch + Model weights)
- **Image Size Limit:** Recommended ≤ 5MB

**Optimization Tips:**
- Compress images before uploading
- Resize to ~512x512 pixels
- Use JPEG format for smaller file size
- Cache model in memory (done automatically)

---

## Examples

### Example 1: Identify Tree with GPS Coordinates
```bash
curl -X POST "https://us-central1-hccms-project.cloudfunctions.net/identifyTreeSpecies" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "front_yard_01",
    "image_url": "gs://hccms-bucket/bark_images/2026-02-05_143000.jpg",
    "location": {
      "latitude": 31.5497,
      "longitude": 77.1703
    }
  }'
```

**Response:**
```json
{
    "success": true,
    "tree_id": "tree_20260205_front_01",
    "species": "Shorea robusta",
    "confidence": 0.8756,
    "confidence_level": "high",
    "carbon_rate_kg_per_month": 2.5,
    "message": "Tree identified as Shorea robusta with 87.6% confidence"
}
```

### Example 2: Multiple Trees in Sequence

Loop through tree images from storage and identify each one:

```python
# Python example
import requests
import json

device_id = "device_001"
image_urls = [
    "gs://bucket/tree1.jpg",
    "gs://bucket/tree2.jpg",
    "gs://bucket/tree3.jpg"
]

location = {"latitude": 31.5, "longitude": 77.1}

for image_url in image_urls:
    response = requests.post(
        "https://us-central1-project.cloudfunctions.net/identifyTreeSpecies",
        json={
            "device_id": device_id,
            "image_url": image_url,
            "location": location
        }
    )
    
    if response.status_code == 201:
        result = response.json()
        print(f"✓ Identified: {result['species']} ({result['confidence']:.1%})")
    else:
        print(f"✗ Error: {response.json()['error']}")
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Device not found" | Register device in Firestore first |
| "Failed to load image" | Check image URL is accessible and valid format |
| Long processing time | Model caches after first call; subsequent calls are faster |
| Low confidence | Try different angle or better lighting, or use high-res image |
| Out of memory | Reduce concurrent requests; model uses ~400MB |

---

## Future Enhancements

- [ ] TensorFlow Lite version for edge inference
- [ ] Additional tree species support
- [ ] Health status assessment (diseased vs healthy bark)
- [ ] Batch identification endpoint
- [ ] Historical trend analysis
- [ ] Model fine-tuning on user-specific trees

---

## References

- **Dataset:** BarkVisionAI (156,001 tree bark images, 13 species)
- **Model:** ResNet50 with 87.42% accuracy
- **Training Details:** See `/BarkVisionAI-main/src/train.py`
- **Original Paper:** [Link to paper on BarkVisionAI]
