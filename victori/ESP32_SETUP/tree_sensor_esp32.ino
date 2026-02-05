/**
 * ESP32 Carbon Credit Tree Sensor System
 * 
 * Hardware Requirements:
 * - ESP32 with WiFi
 * - ESP32-CAM (for image capture)
 * - DHT22 sensor (temperature & humidity)
 * - BH1750 sensor (light intensity)
 * - MQ135 sensor (CO2 levels)
 * - Ultrasonic sensor (tree height estimation)
 * 
 * Libraries:
 * - DHT library
 * - BH1750 library
 * - AsyncHTTPClient
 * - JPEG encoding libraries (for ESP32-CAM)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include "DHT.h"

// ===== WiFi Configuration =====
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// ===== API Configuration =====
const char* webhookURL = "https://your-project.supabase.co/functions/v1/receive-sensor-data";
const char* imageUploadURL = "https://your-project.supabase.co/functions/v1/upload-tree-image";
const char* deviceID = "esp32-001";
const char* apiKey = "your-device-api-key";

// ===== Sensor Pins =====
#define DHTPIN 4
#define DHTTYPE DHT22
#define BH1750_I2C_ADDRESS 0x23
#define MQ135_PIN 34  // ADC pin
#define ECHO_PIN 5
#define TRIG_PIN 18

// ===== Sensor Objects =====
DHT dht(DHTPIN, DHTTYPE);
uint16_t lightLevel = 0;
float co2Level = 0;
float temperature = 0;
float humidity = 0;
float soilMoisture = 0;
float treeHeight = 0;
float treeDBH = 0;  // Diameter at Breast Height (from manual measurement)

// ===== Timing =====
unsigned long lastSensorRead = 0;
unsigned long lastImageCapture = 0;
unsigned long lastWebhookSend = 0;
const unsigned long SENSOR_INTERVAL = 5000;      // 5 seconds
const unsigned long IMAGE_INTERVAL = 300000;     // 5 minutes
const unsigned long WEBHOOK_INTERVAL = 30000;    // 30 seconds

// ===== Camera =====
#ifdef __has_include("esp_camera.h")
#include "esp_camera.h"
bool cameraInitialized = false;

// Camera pin configuration for ESP32-CAM
#define PWDN_GPIO_NUM    32
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27
#define Y9_GPIO_NUM      35
#define Y8_GPIO_NUM      34
#define Y7_GPIO_NUM      39
#define Y6_GPIO_NUM      36
#define Y5_GPIO_NUM      21
#define Y4_GPIO_NUM      19
#define Y3_GPIO_NUM      18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM   25
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22
#endif

// ===== Setup =====
void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=== ESP32 Tree Carbon Sensor System ===");
  
  // Initialize sensors
  initDHT();
  initBH1750();
  initUltrasonicSensor();
  
  // Initialize WiFi
  initWiFi();
  
  // Initialize camera (optional)
  initCamera();
  
  // Test sensor read
  readAllSensors();
}

// ===== Main Loop =====
void loop() {
  unsigned long currentTime = millis();
  
  // Read sensors every SENSOR_INTERVAL
  if (currentTime - lastSensorRead >= SENSOR_INTERVAL) {
    readAllSensors();
    lastSensorRead = currentTime;
  }
  
  // Send sensor data every WEBHOOK_INTERVAL
  if (currentTime - lastWebhookSend >= WEBHOOK_INTERVAL) {
    sendSensorData();
    lastWebhookSend = currentTime;
  }
  
  // Capture and upload image every IMAGE_INTERVAL
  if (cameraInitialized && (currentTime - lastImageCapture >= IMAGE_INTERVAL)) {
    captureAndUploadImage();
    lastImageCapture = currentTime;
  }
  
  delay(100);
}

// ===== WiFi Setup =====
void initWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nFailed to connect to WiFi");
  }
}

// ===== DHT Sensor Initialization =====
void initDHT() {
  Serial.println("Initializing DHT22 sensor...");
  dht.begin();
  delay(1000);
  Serial.println("DHT22 initialized");
}

// ===== BH1750 Light Sensor Initialization =====
void initBH1750() {
  Serial.println("Initializing BH1750 light sensor...");
  Wire.begin();
  Wire.beginTransmission(BH1750_I2C_ADDRESS);
  Wire.write(0x10);  // High resolution mode
  Wire.endTransmission();
  Serial.println("BH1750 initialized");
}

// ===== Ultrasonic Sensor Initialization =====
void initUltrasonicSensor() {
  Serial.println("Initializing ultrasonic sensor...");
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.println("Ultrasonic sensor initialized");
}

// ===== Camera Initialization =====
void initCamera() {
  #ifdef __has_include("esp_camera.h")
  Serial.println("Initializing camera...");
  
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d7 = Y7_GPIO_NUM;
  config.pin_d6 = Y6_GPIO_NUM;
  config.pin_d5 = Y5_GPIO_NUM;
  config.pin_d4 = Y4_GPIO_NUM;
  config.pin_d3 = Y3_GPIO_NUM;
  config.pin_d2 = Y2_GPIO_NUM;
  config.pin_d1 = Y9_GPIO_NUM;
  config.pin_d0 = Y8_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_sioD = SIOD_GPIO_NUM;
  config.pin_sioC = SIOC_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;  // 640x480
  config.jpeg_quality = 12;
  config.fb_count = 1;
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    cameraInitialized = false;
  } else {
    Serial.println("Camera initialized successfully");
    cameraInitialized = true;
  }
  #endif
}

// ===== Read All Sensors =====
void readAllSensors() {
  // Read DHT22
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();
  
  // Read BH1750
  lightLevel = readBH1750();
  
  // Read CO2 (MQ135)
  co2Level = readCO2();
  
  // Measure tree height with ultrasonic sensor
  treeHeight = measureTreeHeight();
  
  // Note: DBH should be measured manually or from camera image analysis
  // For now, use placeholder (would be measured from tree trunk in camera image)
  treeDBH = 30.0;  // Example: 30cm DBH
  
  // Calculate CO2 absorption and O2 release (simplified)
  float co2Absorbed = max(0.0f, (lightLevel / 1000.0f) * (humidity / 100.0f) * 10.0f);
  float o2Released = max(0.0f, co2Absorbed * 0.7f);
  
  Serial.println("\n===== Sensor Data =====");
  Serial.printf("Temperature: %.2f°C\n", temperature);
  Serial.printf("Humidity: %.2f%%\n", humidity);
  Serial.printf("Light Intensity: %d µmol/m²/s\n", lightLevel);
  Serial.printf("CO2 Level: %.2f ppm\n", co2Level);
  Serial.printf("Tree Height: %.2f m\n", treeHeight);
  Serial.printf("Tree DBH: %.2f cm\n", treeDBH);
  Serial.printf("CO2 Absorbed: %.2f ppm\n", co2Absorbed);
  Serial.printf("O2 Released: %.2f ppm\n", o2Released);
}

// ===== Read BH1750 Light Level =====
uint16_t readBH1750() {
  Wire.beginTransmission(BH1750_I2C_ADDRESS);
  Wire.requestFrom(BH1750_I2C_ADDRESS, 2);
  
  if (Wire.available() == 2) {
    uint8_t high = Wire.read();
    uint8_t low = Wire.read();
    return ((high << 8) | low) / 1.2;  // Convert to µmol/m²/s
  }
  return 0;
}

// ===== Read CO2 Level (MQ135) =====
float readCO2() {
  // Simple CO2 estimation from MQ135 sensor
  // Actual calibration depends on sensor and environment
  int rawValue = analogRead(MQ135_PIN);
  float voltage = rawValue / 4095.0 * 3.3;
  float co2Estimate = 400 + (voltage - 1.5) * 100;  // Placeholder formula
  return max(0.0f, co2Estimate);
}

// ===== Measure Tree Height with Ultrasonic Sensor =====
float measureTreeHeight() {
  // Send ultrasonic pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Measure echo duration
  long duration = pulseIn(ECHO_PIN, HIGH);
  
  // Calculate distance (speed of sound = 343 m/s)
  float distance = duration * 0.017;  // cm
  return distance / 100.0;  // Convert to meters
}

// ===== Send Sensor Data via Webhook =====
void sendSensorData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected, skipping webhook");
    return;
  }
  
  HTTPClient http;
  http.begin(webhookURL);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  DynamicJsonDocument doc(1024);
  doc["device_id"] = deviceID;
  doc["api_key"] = apiKey;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = 50;  // Placeholder
  doc["light_intensity"] = lightLevel;
  doc["co2_level"] = co2Level;
  doc["battery"] = 85;  // Placeholder - read from ADC
  doc["rssi"] = WiFi.RSSI();
  doc["dbh"] = treeDBH;
  doc["tree_height"] = treeHeight;
  doc["co2_emitted_ppm"] = 420.0;  // Ambient CO2
  doc["co2_absorbed_ppm"] = max(0.0f, (lightLevel / 1000.0f) * (humidity / 100.0f) * 10.0f);
  doc["o2_released_ppm"] = max(0.0f, (lightLevel / 1000.0f) * (humidity / 100.0f) * 7.0f);
  
  String payload;
  serializeJson(doc, payload);
  
  Serial.print("Sending webhook: ");
  Serial.println(payload);
  
  int httpResponseCode = http.POST(payload);
  
  if (httpResponseCode > 0) {
    Serial.printf("Response Code: %d\n", httpResponseCode);
    String response = http.getString();
    Serial.println("Response: " + response);
  } else {
    Serial.printf("Error: %s\n", http.errorToString(httpResponseCode).c_str());
  }
  
  http.end();
}

// ===== Capture and Upload Image =====
void captureAndUploadImage() {
  #ifdef __has_include("esp_camera.h")
  if (!cameraInitialized) {
    Serial.println("Camera not initialized");
    return;
  }
  
  Serial.println("Capturing image...");
  camera_fb_t* fb = esp_camera_fb_get();
  
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  
  // Convert image to base64
  String imageBase64 = base64_encode(fb->buf, fb->len);
  
  // Create JSON payload
  DynamicJsonDocument doc(1024);
  doc["device_id"] = deviceID;
  doc["api_key"] = apiKey;
  doc["image_base64"] = imageBase64.substring(0, 10000);  // Limit size
  doc["dbh"] = treeDBH;
  doc["height"] = treeHeight;
  doc["location"]["latitude"] = 0.0;  // Add GPS if available
  doc["location"]["longitude"] = 0.0;
  
  String payload;
  serializeJson(doc, payload);
  
  // Send to server
  HTTPClient http;
  http.begin(imageUploadURL);
  http.addHeader("Content-Type", "application/json");
  
  int httpResponseCode = http.POST(payload);
  Serial.printf("Image upload response: %d\n", httpResponseCode);
  
  http.end();
  esp_camera_fb_return(fb);
  #endif
}

// ===== Base64 Encoding Helper =====
String base64_encode(uint8_t* data, size_t len) {
  // Simplified base64 encoding (full implementation recommended)
  const char* base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  String encoded = "";
  
  for (size_t i = 0; i < len; i += 3) {
    uint32_t b = (data[i] << 16) | (data[i + 1] << 8) | data[i + 2];
    encoded += base64_chars[(b >> 18) & 0x3F];
    encoded += base64_chars[(b >> 12) & 0x3F];
    encoded += (i + 1 < len) ? base64_chars[(b >> 6) & 0x3F] : '=';
    encoded += (i + 2 < len) ? base64_chars[b & 0x3F] : '=';
  }
  
  return encoded;
}
