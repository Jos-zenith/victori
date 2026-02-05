#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>

// ================= OLED =================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ================= DHT11 =================
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ================= SENSORS =================
#define SOIL_PIN 35        // Analog
#define LDR_ANALOG_PIN 34  // Analog LDR
#define LDR_DO_PIN 27      // Digital LDR Module (OPTIONAL)

// ================= CALIBRATION VALUES =================
// CHANGE THESE after testing
#define SOIL_DRY 3200
#define SOIL_WET 1200

#define LDR_DARK 4095
#define LDR_BRIGHT 300

unsigned long lastUpdate = 0;
const unsigned long interval = 10000; // 10 seconds

void setup() {
  Serial.begin(115200);

  dht.begin();

  pinMode(LDR_DO_PIN, INPUT);

  // OLED Init
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED not found");
    while (true);
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
}

void loop() {
  if (millis() - lastUpdate >= interval) {
    lastUpdate = millis();

    // ===== READ DHT =====
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // ===== READ SOIL =====
    int soilRaw = analogRead(SOIL_PIN);
    int soilPercent = map(soilRaw, SOIL_DRY, SOIL_WET, 0, 100);
    soilPercent = constrain(soilPercent, 0, 100);

    // ===== READ LDR (ANALOG) =====
    int ldrRaw = analogRead(LDR_ANALOG_PIN);
    int lightPercent = map(ldrRaw, LDR_DARK, LDR_BRIGHT, 0, 100);
    lightPercent = constrain(lightPercent, 0, 100);

    // ===== READ LDR (DIGITAL MODULE) =====
    int ldrDigital = digitalRead(LDR_DO_PIN); // 1 = Bright, 0 = Dark

    // ===== SERIAL DEBUG =====
    Serial.println("---- TREE MODULE DATA ----");
    Serial.print("Temp: "); Serial.print(temperature); Serial.println(" C");
    Serial.print("Humidity: "); Serial.print(humidity); Serial.println(" %");
    Serial.print("Soil: "); Serial.print(soilPercent); Serial.println(" %");
    Serial.print("Light: "); Serial.print(lightPercent); Serial.println(" %");
    Serial.print("LDR DO: "); Serial.println(ldrDigital ? "BRIGHT" : "DARK");
    Serial.println("--------------------------");

    // ===== OLED DISPLAY =====
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);

    display.print("Temp: ");
    display.print(temperature);
    display.println(" C");

    display.print("Hum : ");
    display.print(humidity);
    display.println(" %");

    display.print("Soil: ");
    display.print(soilPercent);
    display.println(" %");

    display.print("Light: ");
    display.print(lightPercent);
    display.println(" %");

    display.print("LDR: ");
    display.println(ldrDigital ? "Bright" : "Dark");

    display.display();
  }
}
