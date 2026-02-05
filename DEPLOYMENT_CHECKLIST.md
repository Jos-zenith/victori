# Deployment Checklist: Real-time Carbon Credit Calculator

## Pre-Deployment (Planning Phase)

### Requirements Assessment
- [ ] Understand Chave allometric equation basics
- [ ] Review ESP32 sensor pinout documentation
- [ ] Plan tree measurement protocol (DBH at 1.3m height)
- [ ] Identify target tree species and their wood densities
- [ ] Determine data collection frequency (recommend 30-second intervals)

### Hardware Preparation
- [ ] Procure ESP32 DevKit
- [ ] Procure DHT22 temperature/humidity sensor
- [ ] Procure BH1750 light intensity sensor
- [ ] Procure VL53L0X or HC-SR04 distance sensor (optional for height)
- [ ] Procure ESP32-CAM module (optional for image capture)
- [ ] Gather soldering equipment and breadboard
- [ ] Verify power supply (5V recommended)

### Software Setup
- [ ] Install Arduino IDE (latest version)
- [ ] Add ESP32 board support to Arduino IDE
- [ ] Install required Arduino libraries:
  - [ ] ArduinoJson
  - [ ] DHT
  - [ ] BH1750
  - [ ] VL53L0X (if using)
  - [ ] esp32-camera (if using ESP32-CAM)

---

## Supabase Configuration

### Database & Webhook Setup
- [ ] Verify Supabase project is created
- [ ] Confirm `sensor_readings` table exists with columns:
  - [ ] `id` (UUID, primary key)
  - [ ] `device_id` (varchar)
  - [ ] `user_id` (UUID)
  - [ ] `temperature` (float)
  - [ ] `humidity` (float)
  - [ ] `light_intensity` (float)
  - [ ] `metadata` (jsonb)
  - [ ] `timestamp` (datetime)
  - [ ] `received_at` (datetime)

- [ ] Confirm `tree_identifications` table exists with:
  - [ ] `species` (varchar)
  - [ ] `confidence` (float)
  - [ ] `image_url` (varchar)

### Functions Deployment
- [ ] Deploy `supabase/functions/receive-sensor-data/index.ts`
  - [ ] Verify function URL is accessible
  - [ ] Test with cURL webhook test
  - [ ] Confirm data appears in `sensor_readings` table

- [ ] Deploy `supabase/functions/upload-tree-image/index.ts`
  - [ ] Configure Supabase Storage bucket: `tree-images`
  - [ ] Set bucket to public access
  - [ ] Test image upload functionality

### Real-time Configuration
- [ ] Enable real-time for `sensor_readings` table in Supabase dashboard
- [ ] Enable real-time for `tree_identifications` table
- [ ] Test real-time subscriptions in browser console

### Authentication
- [ ] Create device API keys in Supabase (or use anon key)
- [ ] Document API keys for ESP32 configuration
- [ ] Set appropriate RLS policies if using row-level security

---

## ESP32 Configuration & Programming

### Sketch Customization
Edit `victori/ESP32_SETUP/tree_sensor_esp32.ino`:

- [ ] **WiFi Configuration (Lines 26-27)**:
  ```cpp
  const char* ssid = "YOUR_ACTUAL_SSID";
  const char* password = "YOUR_ACTUAL_PASSWORD";
  ```

- [ ] **API Configuration (Lines 30-33)**:
  ```cpp
  const char* webhookURL = "https://YOUR-PROJECT.supabase.co/functions/v1/receive-sensor-data";
  const char* deviceID = "esp32-001"; // Unique ID for this device
  const char* apiKey = "YOUR-API-KEY";
  ```

- [ ] **Sensor Pins (Lines 35-41)**:
  - [ ] Verify DHT22 pin is GPIO 4 (or adjust)
  - [ ] Verify BH1750 uses I2C (SDA/SCL)
  - [ ] Verify distance sensor pins

- [ ] **Timing Configuration (Lines 57-59)**:
  - [ ] `SENSOR_INTERVAL`: 5000 (5 seconds)
  - [ ] `IMAGE_INTERVAL`: 300000 (5 minutes)
  - [ ] `WEBHOOK_INTERVAL`: 30000 (30 seconds)

### Hardware Assembly
- [ ] Connect DHT22 to GPIO 4 and GND
- [ ] Connect BH1750 via I2C (SDA=21, SCL=22)
- [ ] Connect distance sensor if used
- [ ] Connect power supply
- [ ] Verify connections with multimeter

### Programming & Upload
- [ ] Connect ESP32 to computer via USB
- [ ] Select correct board in Arduino IDE: "ESP32 Dev Module"
- [ ] Select correct COM port
- [ ] Set baud rate to 115200
- [ ] Compile sketch (verify no errors)
- [ ] Upload sketch to ESP32
- [ ] Monitor serial output at 115200 baud:
  - [ ] Confirm sensor initialization messages
  - [ ] Verify WiFi connection
  - [ ] Check webhook HTTP response codes (200 = success)

### Testing & Verification
- [ ] ESP32 connects to WiFi (check serial: "WiFi connected")
- [ ] DHT22 reads temperature/humidity (check serial output)
- [ ] BH1750 reads light intensity (check serial output)
- [ ] Webhook requests send every 30 seconds
- [ ] Supabase shows new rows in `sensor_readings` table
- [ ] Data includes correct device_id and timestamp

---

## Vue Dashboard Configuration

### Environment Variables
- [ ] Set `VITE_SUPABASE_URL` in `.env.local` or deploy environment
- [ ] Set `VITE_SUPABASE_ANON_KEY` for real-time subscriptions
- [ ] Verify environment variables are loaded (check browser console)

### Dashboard Testing
- [ ] Open dashboard in browser
- [ ] Navigate to Dashboard page
- [ ] Verify "Live ESP32 Data" banner appears (once ESP32 sends data)
- [ ] Check that metric cards update:
  - [ ] Temperature, humidity, light values
  - [ ] DBH and height (if provided)
  - [ ] Health score (0-100%)
  - [ ] Monthly CO₂ offset
  
### Real-time Subscription Verification
- [ ] Open browser DevTools (F12)
- [ ] Go to Console tab
- [ ] Monitor for Supabase subscription messages
- [ ] Verify "sensor_readings_live" channel connects
- [ ] Send test data from ESP32 and verify dashboard updates < 2 seconds

### Chave Calculation Verification
- [ ] Open browser DevTools Console
- [ ] Look for calculated values:
  ```
  [v0] CO2 Monthly: 38.2 kg
  [v0] Health Score: 0.87 (87%)
  ```
- [ ] Manually verify calculation:
  - [ ] Compare to local Python test: `python test_chave.py --dbh 25.5 --height 18`
  - [ ] Values should match within ±1%

---

## Tree Image Analysis (Optional)

### ESP32-CAM Setup
- [ ] Obtain ESP32-CAM module
- [ ] Program ESP32-CAM with capture sketch
- [ ] Configure camera pins in sketch
- [ ] Test image capture (view images in Supabase Storage)

### ML Model Integration
- [ ] Configure tree species ML model (local or cloud)
- [ ] Test model accuracy on sample tree images
- [ ] Integrate model with `upload-tree-image` function
- [ ] Verify species identification in dashboard

### Image Storage
- [ ] Supabase Storage bucket created: `tree-images`
- [ ] Bucket has public access for image URLs
- [ ] Test upload via `upload-tree-image` function
- [ ] Verify images appear in dashboard history

---

## Performance & Optimization

### Data Transmission
- [ ] Verify ESP32 sends data every 30 seconds ✓
- [ ] Monitor network traffic (bandwidth should be minimal)
- [ ] Check battery consumption if running on battery
- [ ] Optimize sensor read frequency if needed

### Dashboard Performance
- [ ] Check browser performance (Console → Performance)
- [ ] Verify real-time updates < 2 seconds
- [ ] Monitor memory usage (should be stable)
- [ ] Test on mobile devices (responsive)

### Database
- [ ] Monitor Supabase function logs for errors
- [ ] Check sensor_readings table row count
- [ ] Verify real-time broadcasts are efficient
- [ ] Set up data retention policy if needed

---

## Security Configuration

### API Keys
- [ ] Device API key is environment-specific
- [ ] API key NOT committed to git
- [ ] API key stored in Supabase Secrets
- [ ] Rotate API keys regularly (quarterly)

### Data Privacy
- [ ] Implement RLS policies for sensor data
- [ ] User can only see their own device data
- [ ] Images stored in private bucket if sensitive
- [ ] GDPR compliance checked

### Network Security
- [ ] Webhook uses HTTPS only
- [ ] Content-Type validation in webhook
- [ ] API key validated on every request
- [ ] CORS headers properly configured

---

## Documentation & Knowledge Transfer

### Documentation Complete
- [ ] QUICKSTART.md reviewed and tested
- [ ] REALTIME_ESP32_SETUP.md is comprehensive
- [ ] IMPLEMENTATION_SUMMARY.md documents architecture
- [ ] TREE_SPECIES_REFERENCE.md covers species data
- [ ] DEPLOYMENT_CHECKLIST.md (this document)

### Code Comments
- [ ] ESP32 sketch has clear comments
- [ ] Webhook functions documented
- [ ] Dashboard calculation logic explained
- [ ] TODO comments for future improvements

### Knowledge Transfer
- [ ] Team trained on Chave equation
- [ ] Team trained on ESP32 setup process
- [ ] Dashboard operation guide created
- [ ] Troubleshooting guide available

---

## Post-Deployment Monitoring

### First 24 Hours
- [ ] Monitor ESP32 connectivity (check serial logs)
- [ ] Verify continuous data flow to Supabase
- [ ] Dashboard displays real-time data correctly
- [ ] No unexpected errors in Supabase logs
- [ ] Battery level stable (if battery powered)

### First Week
- [ ] Review accumulated sensor data quality
- [ ] Verify Chave calculations are reasonable
- [ ] Check for any gaps in data transmission
- [ ] Test long-term real-time stability
- [ ] Review user feedback

### Ongoing Maintenance
- [ ] Weekly: Monitor Supabase logs for errors
- [ ] Weekly: Verify dashboard functionality
- [ ] Monthly: Review CO₂ calculation accuracy
- [ ] Monthly: Backup sensor data
- [ ] Quarterly: Rotate API keys
- [ ] Quarterly: Update firmware if needed

---

## Troubleshooting Quick Reference

### ESP32 Won't Connect to WiFi
- [ ] Check SSID/password are correct
- [ ] Verify WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- [ ] Check signal strength in area
- [ ] Restart ESP32 (press RST button)

### Real-time Data Not Appearing
- [ ] Verify Supabase real-time is enabled
- [ ] Check browser console for subscription errors
- [ ] Verify API keys are correct
- [ ] Test webhook with cURL

### Chave Calculation Wrong
- [ ] Verify DBH > 0 (minimum diameter required)
- [ ] Check wood density is reasonable (0.3 - 1.0)
- [ ] Compare result to test_chave.py output
- [ ] Verify tree height is not 0

### Images Not Uploading
- [ ] Check Supabase Storage bucket exists
- [ ] Verify bucket is public
- [ ] Check image file size (< 25MB)
- [ ] Review function logs in Supabase

---

## Sign-Off

### Project Manager
- [ ] All deliverables completed
- [ ] Documentation reviewed
- [ ] Performance acceptable
- [ ] Ready for production
- [ ] Date: _______________

### Technical Lead
- [ ] Code reviewed and tested
- [ ] Security review passed
- [ ] Performance optimized
- [ ] Monitoring configured
- [ ] Date: _______________

### Client/Stakeholder
- [ ] Requirements met
- [ ] Functionality acceptable
- [ ] Ready to deploy
- [ ] Date: _______________

---

## Version Control

**Implementation Version**: 1.0  
**Deployment Date**: _______________  
**ESP32 Firmware**: tree_sensor_v1.0  
**Dashboard Version**: Carbon Credit Calculator v1.0  
**Documentation Version**: v1.0  

**Future Updates**:
- [ ] Multi-tree support
- [ ] GPS coordinates tracking
- [ ] Cloud storage integration
- [ ] Advanced ML model
- [ ] Mobile app version
