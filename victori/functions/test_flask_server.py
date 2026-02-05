"""Test script for Flask inference server"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:5000"

# Test 1: Health check
print("=" * 60)
print("TEST 1: Health Check")
print("=" * 60)
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: List classes
print("\n" + "=" * 60)
print("TEST 2: List Classes")
print("=" * 60)
response = requests.get(f"{BASE_URL}/classes")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 3: Classify Coconut Tree image
print("\n" + "=" * 60)
print("TEST 3: Classify Coconut Tree Image")
print("=" * 60)
image_path = Path(r"d:\betty\impact\victori\BarkVisionAI-dataset\BarkVisionAI-dataset\src\Coconut Tree\image_00.jpeg")

if image_path.exists():
    with open(image_path, 'rb') as f:
        files = {'image': ('test_image.jpg', f, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/identify", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        print(f"\n✓ Classification successful!")
        print(f"  Species: {result.get('species')}")
        print(f"  Confidence: {result.get('confidence'):.4f}")
    else:
        print(f"\n✗ Classification failed: {result.get('error')}")
else:
    print(f"Image not found: {image_path}")

# Test 4: Classify Mango Tree image
print("\n" + "=" * 60)
print("TEST 4: Classify Mango Tree Image")
print("=" * 60)
mango_path = Path(r"d:\betty\impact\victori\BarkVisionAI-dataset\BarkVisionAI-dataset\src\Mango Tree\image_00.jpeg")

if mango_path.exists():
    with open(mango_path, 'rb') as f:
        files = {'image': ('mango_image.jpg', f, 'image/jpeg')}
        response = requests.post(f"{BASE_URL}/identify", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('success'):
        print(f"\n✓ Classification successful!")
        print(f"  Species: {result.get('species')}")
        print(f"  Confidence: {result.get('confidence'):.4f}")
    else:
        print(f"\n✗ Classification failed: {result.get('error')}")
else:
    print(f"Image not found: {mango_path}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
