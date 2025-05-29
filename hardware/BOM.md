# Bill of Materials (BOM) - Non-Invasive Glucose Monitoring System

## Overview
This document lists all components required to build the non-invasive glucose monitoring prototype. The system uses optical sensing technology with machine learning for glucose level estimation.

---

## Core Components

| Item | Component | Qty | Specifications | Supplier | Price (USD) | Notes |
|------|-----------|-----|----------------|----------|-------------|-------|
| 1 | ESP32 Development Board | 1 | • Dual-core 240MHz<br>• WiFi 802.11b/g/n<br>• Bluetooth 4.2<br>• 4MB Flash | [Adafruit](https://www.adafruit.com/product/3405) | $10.00 | Main microcontroller |
| 2 | MAX30102 Pulse Oximeter | 1 | • I²C Interface<br>• Integrated LEDs<br>• Ambient light rejection<br>• 50Hz-3.2kHz sample rate | [SparkFun](https://www.sparkfun.com/products/14045) | $19.95 | PPG sensor |
| 3 | OLED Display (SSD1306) | 1 | • 128x64 resolution<br>• I²C interface<br>• 0.96" diagonal | [Adafruit](https://www.adafruit.com/product/326) | $12.95 | User interface |
| 4 | MicroSD Card Module | 1 | • SPI interface<br>• Supports up to 32GB<br>• 3.3V/5V compatible | [Amazon](https://amzn.to/3Q1YJ3g) | $2.99 | Data logging |
| 5 | Active Buzzer | 1 | • 5V operation<br>• 85dB sound output<br>• Continuous beep | [Adafruit](https://www.adafruit.com/product/1536) | $1.95 | Alert system |
| 6 | Breadboard | 1 | • 400 tie-points<br>• Self-adhesive back<br>• 6.5" x 2.2" | [SparkFun](https://www.sparkfun.com/products/12002) | $5.95 | Prototyping |
| 7 | Jumper Wires | 1 set | • Male-to-Male<br>• Male-to-Female<br>• Female-to-Female | [Adafruit](https://www.adafruit.com/product/758) | $7.50 | Connections |
| 8 | MicroSD Card | 1 | • 8GB Class 10<br>• FAT32 formatted | [SanDisk](https://amzn.to/3sG0dLb) | $6.99 | Data storage |
| 9 | USB Cable (Micro-B) | 1 | • 1m length<br>• Data + Power | [Amazon](https://amzn.to/3Q2Ld9P) | $3.99 | Programming/Power |
| 10 | Finger Clip Enclosure | 1 | • 3D printable<br>• MAX30102 compatible | [Thingiverse](https://www.thingiverse.com/thing:3476480) | $0.50* | Sensor mount |

\* Cost of filament for 3D printing

**Total Estimated Cost: $72.78**

---

## Optional Components

| Item | Component | Qty | Purpose | Price (USD) |
|------|-----------|-----|---------|-------------|
| 1 | 18650 Battery | 1 | Portable power | $5.00 |
| 2 | Battery Charger Module | 1 | Recharging | $3.50 |
| 3 | Tactile Buttons (6mm) | 3 | User input | $1.50 |
| 4 | 0.1μF Capacitors | 5 | Power filtering | $0.50 |
| 5 | 10kΩ Resistors | 5 | Pull-up/down | $0.30 |
| 6 | TPS61030 Boost Converter | 1 | 3.3V regulation | $2.50 |
| 7 | Enclosure Case | 1 | Project housing | $8.00 |

---

## Connection Diagram

```
ESP32 Pinout:
-----------------
3V3  - MAX30102 VIN, OLED VCC, SD VCC
GND  - MAX30102 GND, OLED GND, SD GND, Buzzer -
GPIO21 - MAX30102 SDA, OLED SDA
GPIO22 - MAX30102 SCL, OLED SCL
GPIO5  - SD Card CS
GPIO18 - SD Card SCK
GPIO23 - SD Card MOSI
GPIO19 - SD Card MISO
GPIO15 - Buzzer +
```

---

## Assembly Instructions

1. **Sensor Setup:**
   - Solder headers to MAX30102 board
   - Mount sensor in 3D-printed finger clip
   - Connect IR/Red LEDs to tissue measurement site

2. **Power Connections:**
   - Connect 3.3V and GND rails on breadboard
   - Wire all components to power rails
   - Add 0.1μF capacitors near sensor power pins

3. **I²C Bus:**
   - Connect SDA (GPIO21) to MAX30102 and OLED
   - Connect SCL (GPIO22) to MAX30102 and OLED
   - Add 10kΩ pull-up resistors (4.7kΩ recommended) to SDA/SCL

4. **SPI Interface:**
   - Connect SD card module:
     - CS → GPIO5
     - SCK → GPIO18
     - MOSI → GPIO23
     - MISO → GPIO19

5. **Alert System:**
   - Connect buzzer positive to GPIO15
   - Connect buzzer negative to GND

6. **Final Assembly:**
   - Secure components on breadboard
   - Insert microSD card
   - Connect USB cable to ESP32
   - Test finger placement in sensor clip

---

## Recommended Suppliers

1. [Adafruit Industries](https://www.adafruit.com) - Quality components with good documentation
2. [SparkFun Electronics](https://www.sparkfun.com) - Reliable sensors and boards
3. [Digi-Key Electronics](https://www.digikey.com) - Wide selection of components
4. [Mouser Electronics](https://www.mouser.com) - Bulk orders and professional components
5. [LCSC Electronics](https://lcsc.com) - Cost-effective options

---

## Safety Considerations

1. **Electrical Safety:**
   - Use 3.3V components only
   - Avoid contact with mains power
   - Implement current limiting where needed

2. **Optical Safety:**
   - MAX30102 is Class I LED product (eye-safe)
   - Do not stare directly into sensor LEDs
   - Limit continuous exposure to <30 minutes

3. **Medical Disclaimer:**
   > ⚠️ **This device is for research purposes only.**  
   > It is not a medical device and should not be used for diagnostic or therapeutic purposes.  
   > Always consult healthcare professionals for medical decisions.

---

## Revision History

| Version | Date       | Changes                |
|---------|------------|------------------------|
| 1.0     | 2023-08-15 | Initial release        |
| 1.1     | 2023-09-01 | Added safety section   |
| 1.2     | 2023-10-15 | Updated suppliers list |
