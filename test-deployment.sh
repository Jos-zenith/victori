#!/bin/bash

echo "=========================================="
echo "HCCMS Deployment Verification Test"
echo "=========================================="
echo ""

# Get Supabase URL from environment
SUPABASE_URL="${SUPABASE_URL:-https://your-project-id.supabase.co}"

echo "Testing Edge Function: receive-sensor-data"
echo "URL: $SUPABASE_URL/functions/v1/receive-sensor-data"
echo ""

# Test sensor data submission
curl -X POST "$SUPABASE_URL/functions/v1/receive-sensor-data" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "device_001",
    "api_key": "test_api_key_12345",
    "temperature": 25.5,
    "humidity": 65.0,
    "soil_moisture": 75.0,
    "light_intensity": 85.0,
    "battery": 95,
    "rssi": -45
  }'

echo ""
echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "If you see a success message above, your deployment is working!"
echo ""
echo "Next steps:"
echo "1. Get your Supabase credentials from: https://supabase.com/dashboard"
echo "2. Update .env file with your credentials"
echo "3. Deploy frontend to hosting service"
echo "4. Update Arduino code with Supabase URL"
