# Non-Invasive Glucose Monitoring System

![images](https://github.com/user-attachments/assets/b18fea99-1175-4f87-bf9f-29e71c01eedc)


A prototype system for non-invasive glucose level estimation using PPG signals from MAX30102 sensor and machine learning algorithms.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Setup Instructions](#setup-instructions)
- [Data Collection Process](#data-collection-process)
- [Machine Learning Training](#machine-learning-training)
- [Deployment](#deployment)
- [Usage](#usage)
- [Data Management](#data-management)
- [Future Improvements](#future-improvements)
- [License](#license)

## Introduction
This project demonstrates a proof-of-concept for non-invasive glucose monitoring using photoplethysmography (PPG) signals. The system captures infrared and red light absorption data from a MAX30102 sensor, processes the signals to extract meaningful features, and uses a machine learning model to estimate glucose levels. This repository contains the Arduino code for the embedded system and Python scripts for model training.

> **Disclaimer**: This is a research prototype only. Not for medical use. Accuracy depends on individual calibration and has not been clinically validated.

## Features
- Real-time PPG signal acquisition from MAX30102 sensor
- Dual-wavelength (IR + Red) optical measurement
- Feature extraction (IR/Red ratio, signal variability, waveform slope)
- Glucose level prediction using linear regression
- OLED display for real-time readings
- Alert system for hypo/hyperglycemia
- SD card data logging
- Cloud data upload via WiFi
- Model update capability

## Hardware Requirements
| Component              | Quantity | Notes                          |
|------------------------|----------|--------------------------------|
| ESP32 Development Board | 1        | Main microcontroller           |
| MAX30102 Sensor        | 1        | PPG sensor for IR/Red signals  |
| SSD1306 OLED Display   | 1        | 128x64 resolution             |
| MicroSD Card Module    | 1        | For data logging              |
| Buzzer                 | 1        | For alert signals             |
| Breadboard & Jumper Wires | As needed | For connections              |
| Power Source           | 1        | 5V power supply or battery    |

## Setup Instructions

### Circuit Connections
| ESP32 Pin | MAX30102 | SSD1306 | SD Module | Buzzer |
|-----------|----------|---------|-----------|--------|
| 3.3V      | VIN      | VCC     | VCC       |        |
| GND       | GND      | GND     | GND       | GND    |
| GPIO 21   | SDA      | SDA     |           |        |
| GPIO 22   | SCL      | SCL     |           |        |
| GPIO 5    |          |         | CS        |        |
| GPIO 18   |          |         | SCK       |        |
| GPIO 23   |          |         | MOSI      |        |
| GPIO 19   |          |         | MISO      |        |
| GPIO 15   |          |         |           | +      |

### Software Installation
1. Install Arduino IDE (v1.8.x or newer)
2. Add ESP32 board support:
   - Add this URL to Preferences > Additional Boards Manager URLs:
     `https://dl.espressif.com/dl/package_esp32_index.json`
   - Install "ESP32" from Boards Manager
3. Install required libraries:
   - `Adafruit MAX3010x Library`
   - `Adafruit SSD1306`
   - `Adafruit GFX Library`
   - `SD`
   - `WiFi`
4. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/glucose-monitor.git
   ```

## Data Collection Process
1. Connect the hardware as shown in the circuit diagram
2. Place finger on the MAX30102 sensor
3. Upload `GlucoseMonitor.ino` to ESP32
4. Open Serial Monitor (115200 baud)
5. In Training Mode:
   - System captures PPG signals every 5 seconds
   - Features are displayed on OLED
   - Enter reference glucose value via Serial Monitor when prompted
   - Data is saved to SD card and uploaded to cloud
6. Collect data across different physiological states (fasting, post-meal, etc.)

## Machine Learning Training
1. Collect training data on SD card as CSV files
2. Transfer data to computer
3. Run the Python training script:
   ```bash
   pip install pandas numpy scikit-learn
   python train_model.py
   ```
4. The script will:
   - Load and preprocess collected data
   - Train a linear regression model
   - Generate model coefficients
   - Evaluate model performance
   - Save coefficients to `model.csv`
5. Copy `model.csv` to SD card root directory

## Deployment
1. Place `model.csv` on SD card
2. Switch system to Prediction Mode (modify code):
   ```cpp
   // Change in setup()
   currentMode = PREDICTION;
   ```
3. Upload modified code to ESP32
4. System will:
   - Load model coefficients during startup
   - Capture PPG signals in real-time
   - Extract features and predict glucose levels
   - Display results on OLED
   - Trigger alerts when thresholds are exceeded
   - Log prediction data to SD card

## Usage
1. Power on the system
2. Place finger steadily on sensor
3. Wait for 10-20 seconds for stable readings
4. Interpret results:
   - Normal: 70-180 mg/dL
   - Hypoglycemia alert: <70 mg/dL (buzzer sounds)
   - Hyperglycemia alert: >180 mg/dL (buzzer sounds)
5. For continuous monitoring:
   - System updates prediction every 5 seconds
   - Data logs to SD card every minute
   - Cloud uploads occur every 10 minutes

## Data Management
### SD Card Structure
```
/SD_CARD_ROOT
  ├── /training.csv       # Training data (features + reference values)
  ├── /predictions.csv    # Prediction logs
  ├── /model.csv          # Current model coefficients
  └── /backup/            # Archived data files
```

### Cloud Integration
Data is sent to a REST API endpoint in JSON format:
```json
{
  "timestamp": 1678901234567,
  "ratio": 1.2345,
  "variability": 45.67,
  "slope": 12.34,
  "glucose": 125.0,
  "prediction": 128.5
}
```
To configure your endpoint:
```cpp
// In the Arduino code
const char* serverUrl = "http://your-api-endpoint.com/data";
```

## Future Improvements
1. Implement motion artifact detection
2. Add temperature compensation
3. Include heart rate variability features
4. Develop TinyML model with TensorFlow Lite
5. Create mobile app for calibration and visualization
6. Implement user authentication for cloud data
7. Add battery management system
8. Develop enclosure for wearable use

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
