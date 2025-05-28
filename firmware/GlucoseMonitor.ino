#include <Wire.h>
#include "MAX30105.h"
#include <Adafruit_SSD1306.h>
#include <Adafruit_GFX.h>
#include <SD.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Constants and Configuration
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SAMPLE_WINDOW 2000  // 2-second sampling window
#define FEATURE_INTERVAL 5000  // Feature extraction every 5 seconds
#define SAMPLE_RATE 100  // Samples per second
#define BUFFER_SIZE (SAMPLE_WINDOW / 1000 * SAMPLE_RATE)
#define SD_CS 5
#define MODEL_UPDATE_INTERVAL 600000  // 10 minutes for model updates

// Alert Thresholds
const float HYPERGLYCEMIA_THRESHOLD = 180.0;  // mg/dL
const float HYPOGLYCEMIA_THRESHOLD = 70.0;   // mg/dL

// WiFi Credentials
const char* ssid = "your_SSID";
const char* password = "your_PASSWORD";
const char* serverUrl = "http://your-server.com/api/data";

// Global Variables
MAX30105 particleSensor;
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

float irBuffer[BUFFER_SIZE];
float redBuffer[BUFFER_SIZE];
long sampleTimestamps[BUFFER_SIZE];
int bufferIndex = 0;
unsigned long lastFeatureTime = 0;
unsigned long lastUploadTime = 0;

// Machine Learning Model Parameters (To be updated from cloud)
float modelCoefficients[] = {0.0, 0.0, 0.0, 0.0};  // {intercept, ratio, variability, slope}
bool newModelAvailable = false;

// System State
enum SystemMode {TRAINING, PREDICTION};
SystemMode currentMode = TRAINING;
float lastGlucosePrediction = 0.0;

void setup() {
  Serial.begin(115200);
  
  // Initialize Display
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0,0);
  display.println("Glucose Monitor");
  display.display();
  delay(2000);

  // Initialize Sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println(F("MAX30102 not found"));
    while (1);
  }
  
  // Configure Sensor
  byte ledBrightness = 0x1F;
  byte sampleAverage = 4;
  byte ledMode = 2;  // Red + IR
  int sampleRate = SAMPLE_RATE;
  int pulseWidth = 411;
  int adcRange = 4096;
  
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);

  // Initialize SD Card
  if (!SD.begin(SD_CS)) {
    Serial.println(F("SD card initialization failed!"));
  }

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  
  // Load initial model parameters
  loadModelFromSD();
}

void loop() {
  // Check for new model updates
  if (millis() - lastUploadTime > MODEL_UPDATE_INTERVAL) {
    fetchUpdatedModel();
    lastUploadTime = millis();
  }

  // Capture PPG Data
  if (bufferIndex < BUFFER_SIZE) {
    irBuffer[bufferIndex] = particleSensor.getIR();
    redBuffer[bufferIndex] = particleSensor.getRed();
    sampleTimestamps[bufferIndex] = millis();
    bufferIndex++;
    delay(1000/SAMPLE_RATE);
  } else {
    // Shift buffer (FIFO)
    for(int i=0; i<BUFFER_SIZE-1; i++) {
      irBuffer[i] = irBuffer[i+1];
      redBuffer[i] = redBuffer[i+1];
      sampleTimestamps[i] = sampleTimestamps[i+1];
    }
    bufferIndex = BUFFER_SIZE-1;
  }

  // Feature Extraction
  if (millis() - lastFeatureTime > FEATURE_INTERVAL) {
    float features[3] = {0};
    extractFeatures(features);
    
    if (currentMode == TRAINING) {
      handleTrainingMode(features);
    } else {
      handlePredictionMode(features);
    }
    
    lastFeatureTime = millis();
  }
}

void extractFeatures(float* features) {
  // 1. IR/Red Ratio
  float irMean = 0, redMean = 0;
  for(int i=0; i<BUFFER_SIZE; i++) {
    irMean += irBuffer[i];
    redMean += redBuffer[i];
  }
  irMean /= BUFFER_SIZE;
  redMean /= BUFFER_SIZE;
  features[0] = irMean / redMean;

  // 2. Signal Variability (RMSSD)
  float irVariability = 0;
  for(int i=1; i<BUFFER_SIZE; i++) {
    float diff = irBuffer[i] - irBuffer[i-1];
    irVariability += diff * diff;
  }
  features[1] = sqrt(irVariability / (BUFFER_SIZE-1));

  // 3. Waveform Slope
  int maxIndex = 0, minIndex = 0;
  float maxVal = irBuffer[0], minVal = irBuffer[0];
  for(int i=1; i<BUFFER_SIZE; i++) {
    if(irBuffer[i] > maxVal) {
      maxVal = irBuffer[i];
      maxIndex = i;
    }
    if(irBuffer[i] < minVal) {
      minVal = irBuffer[i];
      minIndex = i;
    }
  }
  if (maxIndex > minIndex && (maxIndex - minIndex) > 5) {
    features[2] = (maxVal - minVal) / (sampleTimestamps[maxIndex] - sampleTimestamps[minIndex]) * 1000;
  } else {
    features[2] = 0.0;
  }
}

void handleTrainingMode(float* features) {
  display.clearDisplay();
  display.setCursor(0,0);
  display.println("Training Mode");
  display.print("Features:");
  display.print(features[0], 4);
  display.print(", ");
  display.print(features[1], 2);
  display.print(", ");
  display.println(features[2], 2);
  display.println("Enter reference glucose");
  display.display();

  if (Serial.available() > 0) {
    float refGlucose = Serial.parseFloat();
    logTrainingData(features, refGlucose);
  }
}

void handlePredictionMode(float* features) {
  // Predict glucose using linear model: y = b0 + b1*x1 + b2*x2 + b3*x3
  lastGlucosePrediction = modelCoefficients[0] + 
                         modelCoefficients[1] * features[0] +
                         modelCoefficients[2] * features[1] +
                         modelCoefficients[3] * features[2];
  
  // Display results
  display.clearDisplay();
  display.setCursor(0,0);
  display.print("Glucose: ");
  display.print(lastGlucosePrediction, 1);
  display.println(" mg/dL");
  
  // Alert system
  if (lastGlucosePrediction > HYPERGLYCEMIA_THRESHOLD) {
    display.println("HIGH GLUCOSE!");
    display.println("Seek attention");
    tone(BUZZER_PIN, 1000, 500);
  } else if (lastGlucosePrediction < HYPOGLYCEMIA_THRESHOLD) {
    display.println("LOW GLUCOSE!");
    display.println("Consume sugar");
    tone(BUZZER_PIN, 800, 500);
  }
  
  display.display();
  logPredictionData(features, lastGlucosePrediction);
}

void logTrainingData(float* features, float refGlucose) {
  // SD Card Logging
  File dataFile = SD.open("/training.csv", FILE_APPEND);
  if (dataFile) {
    dataFile.print(millis());
    dataFile.print(",");
    dataFile.print(features[0], 6);
    dataFile.print(",");
    dataFile.print(features[1], 4);
    dataFile.print(",");
    dataFile.print(features[2], 2);
    dataFile.print(",");
    dataFile.println(refGlucose, 1);
    dataFile.close();
  }

  // Cloud Upload
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    String payload = "{\"timestamp\":" + String(millis()) + 
                    ",\"ratio\":" + String(features[0], 6) +
                    ",\"variability\":" + String(features[1], 4) +
                    ",\"slope\":" + String(features[2], 2) +
                    ",\"glucose\":" + String(refGlucose, 1) + "}";
    
    int httpCode = http.POST(payload);
    http.end();
  }
}

void logPredictionData(float* features, float glucose) {
  // Similar implementation to logTrainingData but for predictions
  // ...
}

void loadModelFromSD() {
  File modelFile = SD.open("/model.csv");
  if (modelFile) {
    String line = modelFile.readStringUntil('\n');
    sscanf(line.c_str(), "%f,%f,%f,%f", 
           &modelCoefficients[0], &modelCoefficients[1],
           &modelCoefficients[2], &modelCoefficients[3]);
    modelFile.close();
    newModelAvailable = true;
  }
}

void fetchUpdatedModel() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("http://your-server.com/latest-model");
    int httpCode = http.GET();
    
    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      sscanf(payload.c_str(), "%f,%f,%f,%f", 
             &modelCoefficients[0], &modelCoefficients[1],
             &modelCoefficients[2], &modelCoefficients[3]);
      
      // Save to SD card
      File modelFile = SD.open("/model.csv", FILE_WRITE);
      if (modelFile) {
        modelFile.println(payload);
        modelFile.close();
      }
      newModelAvailable = true;
    }
    http.end();
  }
}
