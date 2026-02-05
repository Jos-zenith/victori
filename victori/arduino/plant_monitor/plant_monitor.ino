/**
 * HCCMS - Household Carbon Credit Monitoring System
 * ESP32 Firmware v2.1.0
 *
 * Sensors:
 *   - DHT11 (Temperature & Humidity)
 *   - Soil Moisture Sensor (Analog)
 *   - pH Sensor (Analog)
 *   - LDR (Sunlight Intensity - Analog + Digital)
 *   - MQ135 Gas Sensor (Vehicle CO2 Emission)
 *   - ESP32-CAM Module (Plant Health / Bark Analysis)
 *
 * Communication:
 *   - WebSocket server on port 81
 *   - HTTP REST API on port 80
 *   - JSON-formatted sensor data
 *
 * The ESP32 sends sensor readings to the Vue frontend
 * via WebSocket (primary) or HTTP polling (fallback).
 */

#include <WiFi.h>
#include <WebServer.h>
#include <WebSocketsServer.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ==================== WiFi CONFIG ====================
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ==================== OLED ====================
#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ==================== DHT11 ====================
#define DHTPIN  4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ==================== SENSOR PINS ====================
#define SOIL_PIN       35   // Analog - Soil Moisture
#define LDR_ANALOG_PIN 34   // Analog - LDR
#define LDR_DO_PIN     27   // Digital - LDR Module (optional)
#define PH_PIN         32   // Analog - pH Sensor
#define MQ135_PIN      33   // Analog - MQ135 Gas Sensor

// ==================== CALIBRATION ====================
// Soil Moisture
#define SOIL_DRY  3200
#define SOIL_WET  1200

// LDR
#define LDR_DARK   4095
#define LDR_BRIGHT 300

// pH Sensor calibration
// Adjust these after calibrating with pH 4.0 and pH 7.0 buffer solutions
#define PH_OFFSET  0.0
#define PH_SLOPE   -5.7  // mV per pH unit

// MQ135 calibration
// R0 = sensor resistance in clean air (calibrate first)
#define MQ135_R0          76.63
#define MQ135_RL          10.0   // Load resistance in kOhm
// CO2 curve constants (from datasheet)
#define MQ135_CO2_A       116.6020682
#define MQ135_CO2_B       -2.769034857

// ==================== PAR CONVERSION ====================
// Convert LDR percentage to approximate PAR (micromol/m^2/s)
// Full sunlight ~ 2000 umol, LDR saturates much earlier
// This is a rough approximation; use a proper PAR sensor for accuracy
#define PAR_MAX 1200.0

// ==================== CO2 ABSORPTION MODEL ====================
// Simplified model: trees absorb CO2 proportional to sunlight & conditions
// Base absorption rate per tree (ppm equivalent at sensor distance)
#define CO2_ABSORPTION_BASE 320.0
#define O2_RELEASE_BASE     180.0

// ==================== SERVER ====================
WebServer server(80);
WebSocketsServer webSocket(81);

// ==================== TIMING ====================
unsigned long lastSensorRead  = 0;
unsigned long lastWsSend      = 0;
unsigned long lastHeartbeat   = 0;
const unsigned long SENSOR_INTERVAL    = 3000;  // 3 seconds
const unsigned long WS_SEND_INTERVAL   = 3000;  // 3 seconds
const unsigned long HEARTBEAT_INTERVAL = 30000; // 30 seconds

// ==================== SENSOR DATA ====================
struct SensorData {
  float temperature;
  float humidity;
  float soilMoisture;     // percentage
  float lightIntensity;   // micromol/m^2/s (PAR approximation)
  float ph;
  float co2Emitted;       // ppm (from MQ135)
  float co2Absorbed;      // ppm (calculated)
  float o2Released;       // ppm (calculated)
  float batteryLevel;
} sensorData;

// ==================== FUNCTION DECLARATIONS ====================
void readSensors();
void sendSensorDataWS();
void sendHeartbeat();
void handleRoot();
void handleSensorAPI();
void handleCaptureAPI();
void handleHealthAPI();
void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length);
float readMQ135CO2();
float readPH();
float calculateCO2Absorbed(float lightPercent, float temperature, float humidity, float soilMoisture);
float calculateO2Released(float co2Absorbed);
String buildSensorJSON();
void updateOLED();

// ==================== SETUP ====================
void setup() {
  Serial.begin(115200);
  Serial.println("\n========== HCCMS Sensor Hub v2.1.0 ==========");

  // Initialize sensors
  dht.begin();
  pinMode(LDR_DO_PIN, INPUT);
  pinMode(MQ135_PIN, INPUT);
  pinMode(PH_PIN, INPUT);

  // Initialize OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("[WARN] OLED not found - continuing without display");
  } else {
    display.clearDisplay();
    display.setTextColor(SSD1306_WHITE);
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.println("HCCMS v2.1.0");
    display.println("Connecting WiFi...");
    display.display();
  }

  // Connect to WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[WiFi] Connecting");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] Connected! IP: %s\n", WiFi.localIP().toString().c_str());

    display.clearDisplay();
    display.setCursor(0, 0);
    display.println("HCCMS v2.1.0");
    display.print("IP: ");
    display.println(WiFi.localIP().toString());
    display.println("WebSocket: :81");
    display.println("HTTP API: :80");
    display.display();
  } else {
    Serial.println("\n[WiFi] Connection failed - running offline");
  }

  // Setup HTTP server routes
  server.on("/", handleRoot);
  server.on("/api/sensors", HTTP_GET, handleSensorAPI);
  server.on("/api/health", HTTP_GET, handleHealthAPI);
  server.on("/capture", HTTP_GET, handleCaptureAPI);

  // Enable CORS
  server.enableCORS(true);
  server.begin();
  Serial.println("[HTTP] Server started on port 80");

  // Setup WebSocket server
  webSocket.begin();
  webSocket.onEvent(webSocketEvent);
  Serial.println("[WS] WebSocket server started on port 81");

  // Initialize battery level (if using battery monitoring)
  sensorData.batteryLevel = 100.0;

  Serial.println("========== System Ready ==========\n");
  delay(2000);
}

// ==================== LOOP ====================
void loop() {
  server.handleClient();
  webSocket.loop();

  unsigned long now = millis();

  // Read sensors at interval
  if (now - lastSensorRead >= SENSOR_INTERVAL) {
    lastSensorRead = now;
    readSensors();
    updateOLED();
  }

  // Send via WebSocket at interval
  if (now - lastWsSend >= WS_SEND_INTERVAL) {
    lastWsSend = now;
    sendSensorDataWS();
  }

  // Send heartbeat
  if (now - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    lastHeartbeat = now;
    sendHeartbeat();
  }
}

// ==================== SENSOR READING ====================
void readSensors() {
  // DHT11 - Temperature & Humidity
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (!isnan(temp)) sensorData.temperature = temp;
  if (!isnan(hum))  sensorData.humidity = hum;

  // Soil Moisture Sensor
  int soilRaw = analogRead(SOIL_PIN);
  sensorData.soilMoisture = constrain(map(soilRaw, SOIL_DRY, SOIL_WET, 0, 100), 0, 100);

  // LDR - Sunlight Intensity (convert to approximate PAR)
  int ldrRaw = analogRead(LDR_ANALOG_PIN);
  float lightPercent = constrain(map(ldrRaw, LDR_DARK, LDR_BRIGHT, 0, 100), 0, 100);
  sensorData.lightIntensity = (lightPercent / 100.0) * PAR_MAX;

  // pH Sensor
  sensorData.ph = readPH();

  // MQ135 - Vehicle CO2 Emissions
  sensorData.co2Emitted = readMQ135CO2();

  // Calculated values based on environmental conditions
  sensorData.co2Absorbed = calculateCO2Absorbed(
    lightPercent, sensorData.temperature, sensorData.humidity, sensorData.soilMoisture
  );
  sensorData.o2Released = calculateO2Released(sensorData.co2Absorbed);

  // Debug output
  Serial.println("---- HCCMS Sensor Reading ----");
  Serial.printf("  Temp: %.1f C\n", sensorData.temperature);
  Serial.printf("  Humidity: %.1f %%\n", sensorData.humidity);
  Serial.printf("  Soil: %.1f %%\n", sensorData.soilMoisture);
  Serial.printf("  Light: %.1f umol/m2/s\n", sensorData.lightIntensity);
  Serial.printf("  pH: %.2f\n", sensorData.ph);
  Serial.printf("  CO2 Emitted: %.1f ppm\n", sensorData.co2Emitted);
  Serial.printf("  CO2 Absorbed: %.1f ppm\n", sensorData.co2Absorbed);
  Serial.printf("  O2 Released: %.1f ppm\n", sensorData.o2Released);
  Serial.println("------------------------------");
}

// ==================== pH SENSOR ====================
float readPH() {
  // Average multiple readings for stability
  long total = 0;
  for (int i = 0; i < 10; i++) {
    total += analogRead(PH_PIN);
    delay(10);
  }
  float avgVoltage = (total / 10.0) * (3.3 / 4095.0);

  // Convert voltage to pH (calibrate with known buffer solutions)
  // Neutral pH 7.0 ~ 1.65V on ESP32 ADC
  float ph = 7.0 + ((1.65 - avgVoltage) / (PH_SLOPE / 1000.0)) + PH_OFFSET;

  return constrain(ph, 0.0, 14.0);
}

// ==================== MQ135 CO2 SENSOR ====================
float readMQ135CO2() {
  // Average multiple readings
  long total = 0;
  for (int i = 0; i < 10; i++) {
    total += analogRead(MQ135_PIN);
    delay(10);
  }
  float avgRaw = total / 10.0;

  // Convert to resistance ratio
  float voltage = avgRaw * (3.3 / 4095.0);
  float rs = ((3.3 * MQ135_RL) / voltage) - MQ135_RL;
  float ratio = rs / MQ135_R0;

  // Calculate CO2 ppm using the power regression from datasheet
  // ppm = A * (Rs/R0)^B
  float ppm = MQ135_CO2_A * pow(ratio, MQ135_CO2_B);

  return constrain(ppm, 300.0, 5000.0);
}

// ==================== CO2 ABSORPTION MODEL ====================
/**
 * Simplified model for tree CO2 absorption based on environmental conditions.
 * In reality, this would use the Chave equation and photosynthesis models.
 *
 * Factors:
 *   - Sunlight drives photosynthesis (primary factor)
 *   - Temperature affects enzyme activity
 *   - Humidity affects stomatal opening
 *   - Soil moisture affects water availability
 */
float calculateCO2Absorbed(float lightPercent, float temperature, float humidity, float soilMoisture) {
  float base = CO2_ABSORPTION_BASE;

  // Sunlight factor (0.2 - 1.5)
  float lightFactor = 0.2 + (lightPercent / 100.0) * 1.3;

  // Temperature factor (optimal 20-30 C)
  float tempFactor;
  if (temperature >= 20 && temperature <= 30) {
    tempFactor = 1.2;
  } else if (temperature >= 15 && temperature <= 35) {
    tempFactor = 1.0;
  } else {
    tempFactor = 0.5;
  }

  // Humidity factor
  float humFactor;
  if (humidity >= 40 && humidity <= 80) {
    humFactor = 1.1;
  } else {
    humFactor = 0.8;
  }

  // Soil moisture factor
  float soilFactor;
  if (soilMoisture >= 30 && soilMoisture <= 70) {
    soilFactor = 1.1;
  } else {
    soilFactor = 0.7;
  }

  return base * lightFactor * tempFactor * humFactor * soilFactor;
}

// ==================== O2 RELEASE MODEL ====================
float calculateO2Released(float co2Absorbed) {
  // Photosynthesis: 6CO2 + 6H2O -> C6H12O6 + 6O2
  // Molar ratio CO2:O2 is 1:1
  // But in ppm terms, O2 release is slightly different due to molecular weights
  // O2 (32 g/mol) vs CO2 (44 g/mol)
  return co2Absorbed * (32.0 / 44.0) * 1.1; // slight efficiency factor
}

// ==================== BUILD JSON ====================
String buildSensorJSON() {
  StaticJsonDocument<512> doc;

  doc["type"]       = "sensor_data";
  doc["deviceId"]   = "esp32-001";
  doc["timestamp"]  = millis();

  JsonObject payload = doc.createNestedObject("payload");
  payload["temperature"]    = round(sensorData.temperature * 10.0) / 10.0;
  payload["humidity"]       = round(sensorData.humidity * 10.0) / 10.0;
  payload["soilMoisture"]   = round(sensorData.soilMoisture * 10.0) / 10.0;
  payload["lightIntensity"] = round(sensorData.lightIntensity * 10.0) / 10.0;
  payload["ph"]             = round(sensorData.ph * 100.0) / 100.0;
  payload["co2Emitted"]     = round(sensorData.co2Emitted * 10.0) / 10.0;
  payload["co2Absorbed"]    = round(sensorData.co2Absorbed * 10.0) / 10.0;
  payload["o2Released"]     = round(sensorData.o2Released * 10.0) / 10.0;
  payload["timestamp"]      = String(millis());

  String jsonStr;
  serializeJson(doc, jsonStr);
  return jsonStr;
}

// ==================== WEBSOCKET ====================
void webSocketEvent(uint8_t num, WStype_t type, uint8_t* payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.printf("[WS] Client #%u disconnected\n", num);
      break;
    case WStype_CONNECTED:
      Serial.printf("[WS] Client #%u connected from %s\n", num,
                     webSocket.remoteIP(num).toString().c_str());
      // Send current data immediately
      webSocket.sendTXT(num, buildSensorJSON());
      break;
    case WStype_TEXT:
      Serial.printf("[WS] Received from #%u: %s\n", num, payload);
      // Handle commands from frontend (e.g., "capture" for camera)
      if (String((char*)payload) == "capture") {
        // Trigger camera capture (if ESP32-CAM)
        Serial.println("[CAM] Capture requested via WebSocket");
      }
      break;
  }
}

void sendSensorDataWS() {
  String json = buildSensorJSON();
  webSocket.broadcastTXT(json);
}

void sendHeartbeat() {
  StaticJsonDocument<256> doc;
  doc["type"]     = "heartbeat";
  doc["deviceId"] = "esp32-001";

  JsonObject payload = doc.createNestedObject("payload");
  payload["battery"]  = sensorData.batteryLevel;
  payload["uptime"]   = millis() / 1000;
  payload["freeHeap"] = ESP.getFreeHeap();
  payload["rssi"]     = WiFi.RSSI();

  String json;
  serializeJson(doc, json);
  webSocket.broadcastTXT(json);
}

// ==================== HTTP HANDLERS ====================
void handleRoot() {
  String html = "<!DOCTYPE html><html><head><title>HCCMS Sensor Hub</title></head><body>";
  html += "<h1>HCCMS Sensor Hub v2.1.0</h1>";
  html += "<p>WebSocket: ws://" + WiFi.localIP().toString() + ":81/ws</p>";
  html += "<p>Sensor API: <a href='/api/sensors'>/api/sensors</a></p>";
  html += "<p>Health: <a href='/api/health'>/api/health</a></p>";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void handleSensorAPI() {
  // Return flat sensor data JSON for HTTP polling
  StaticJsonDocument<512> doc;

  doc["temperature"]    = round(sensorData.temperature * 10.0) / 10.0;
  doc["humidity"]       = round(sensorData.humidity * 10.0) / 10.0;
  doc["soilMoisture"]   = round(sensorData.soilMoisture * 10.0) / 10.0;
  doc["lightIntensity"] = round(sensorData.lightIntensity * 10.0) / 10.0;
  doc["ph"]             = round(sensorData.ph * 100.0) / 100.0;
  doc["co2Emitted"]     = round(sensorData.co2Emitted * 10.0) / 10.0;
  doc["co2Absorbed"]    = round(sensorData.co2Absorbed * 10.0) / 10.0;
  doc["o2Released"]     = round(sensorData.o2Released * 10.0) / 10.0;
  doc["timestamp"]      = String(millis());

  String json;
  serializeJson(doc, json);

  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

void handleCaptureAPI() {
  // ESP32-CAM capture endpoint
  // If using ESP32-CAM, this would capture and return a JPEG image
  // For standard ESP32 without camera, return a message
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", "{\"error\":\"Camera not available on this board. Use ESP32-CAM.\"}");
}

void handleHealthAPI() {
  StaticJsonDocument<256> doc;
  doc["status"]   = "healthy";
  doc["service"]  = "HCCMS Sensor Hub";
  doc["version"]  = "2.1.0";
  doc["uptime"]   = millis() / 1000;
  doc["freeHeap"] = ESP.getFreeHeap();
  doc["rssi"]     = WiFi.RSSI();
  doc["ip"]       = WiFi.localIP().toString();

  String json;
  serializeJson(doc, json);

  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send(200, "application/json", json);
}

// ==================== OLED DISPLAY ====================
void updateOLED() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setCursor(0, 0);

  display.printf("T:%.1fC H:%.0f%%\n", sensorData.temperature, sensorData.humidity);
  display.printf("Soil:%.0f%% pH:%.1f\n", sensorData.soilMoisture, sensorData.ph);
  display.printf("Light:%.0f umol\n", sensorData.lightIntensity);
  display.printf("CO2e:%.0f CO2a:%.0f\n", sensorData.co2Emitted, sensorData.co2Absorbed);
  display.printf("O2:%.0f ppm\n", sensorData.o2Released);

  // Connection status
  display.setCursor(0, 48);
  if (WiFi.status() == WL_CONNECTED) {
    display.printf("IP:%s\n", WiFi.localIP().toString().c_str());
    display.printf("WS:%d clients", webSocket.connectedClients());
  } else {
    display.println("WiFi: Disconnected");
  }

  display.display();
}
