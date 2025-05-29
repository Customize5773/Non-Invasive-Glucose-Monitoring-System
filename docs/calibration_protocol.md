# Calibration Protocol for Non-Invasive Glucose Monitor

## Overview
Proper calibration is essential for accurate glucose predictions. This protocol outlines the procedure for collecting paired PPG-glucose data to train the machine learning model. Follow these steps precisely for optimal results.

## Pre-Calibration Requirements
1. **Device Preparation:**
   - Fully charge ESP32 or connect to stable power
   - Insert formatted microSD card (FAT32)
   - Verify sensor alignment in finger clip
   - Ensure firmware is in Training Mode

2. **Subject Preparation:**
   - No caffeine/alcohol 8 hours before
   - Avoid hand lotions/creams
   - Normal hydration
   - Fast for 8 hours (overnight)

## Calibration Procedure

### Step 1: Baseline Measurement
1. Take fasting reference glucose measurement with FDA-approved glucometer
2. Note exact time and glucose value
3. Place index finger in sensor clip
4. Collect 2 minutes of PPG data (system automatically logs)
5. Label data: `FASTING_<glucose_value>_<timestamp>`

### Step 2: Post-Prandial Measurements
| Time After Meal | Procedure |
|-----------------|-----------|
| 30 minutes      | 1. Measure reference glucose<br>2. Collect 2-min PPG data<br>3. Label: `POSTPRANDIAL_30_<value>` |
| 60 minutes      | Repeat above procedure |
| 90 minutes      | Repeat above procedure |
| 120 minutes     | Repeat above procedure |

### Step 3: Glucose Challenge (Optional)
```python
# Recommended glucose intake
def calculate_glucose_dose(weight_kg):
    return min(75, 1.5 * weight_kg)  # grams of glucose
```

1. Administer glucose solution (oral)
2. Repeat measurements every 15 minutes for 3 hours
3. Label: `CHALLENGE_<minutes>_<value>`

## Data Collection Standards
1. **Environmental Conditions:**
   - Temperature: 20-25°C
   - Humidity: 40-60% RH
   - Ambient light: < 500 lux

2. **Sensor Placement:**
   ![Finger Placement](assets/images/finger_placement.jpg)
   - Index or middle finger
   - Consistent pressure (use spring-loaded clip)
   - No nail polish

3. **Motion Control:**
   - Use armrest during measurements
   - No talking or movement
   - Start logging after 10s stabilization

## Data Requirements
| Parameter | Minimum | Ideal |
|-----------|---------|-------|
| Subjects | 5 | 20+ |
| Data points per subject | 8 | 25+ |
| Glucose range coverage | 70-180 mg/dL | 50-300 mg/dL |
| Total paired samples | 40 | 500+ |

## Quality Control
1. **Signal Validation:**
   ```python
   # Python validation criteria
   def validate_ppg(ir_signal, red_signal):
       ir_amplitude = max(ir_signal) - min(ir_signal)
       red_amplitude = max(red_signal) - min(red_signal)
       
       valid = (
           (ir_amplitude > 5000) and 
           (red_amplitude > 3000) and
           (np.std(ir_signal) > 100)
       )
       return valid
   ```

2. **Rejection Criteria:**
   - Motion artifacts visible in waveform
   - Poor perfusion (amplitude < 3000 counts)
   - Signal dropout > 10%
   - Glucometer error codes

## File Naming Convention
`<SubjectID>_<Condition>_<GlucoseValue>_<Timestamp>.csv`
Example: `S02_FASTING_89_20230815T0730.csv`

## Post-Processing
1. Combine all CSV files:
   ```bash
   cat *.csv > combined_calibration_data.csv
   ```
2. Verify dataset balance:
   ![Glucose Distribution](assets/images/glucose_distribution.png)

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Low signal amplitude | 1. Clean sensor window<br>2. Warm finger<br>3. Adjust clip tension |
| Signal dropout | 1. Check wiring<br>2. Reduce sample rate<br>3. Add capacitors (0.1µF) |
| High variability | 1. Stabilize arm<br>2. Darken environment<br>3. Wait longer post-meal |
