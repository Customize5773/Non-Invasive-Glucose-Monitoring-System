### Key Features:

1. **Data Handling:**
   - Loads single CSV files or entire directories of training data
   - Handles missing values and outliers
   - Adds derived features (pulse rate, AC/DC ratio)

2. **Preprocessing:**
   - Median imputation for missing values
   - Outlier removal using IQR method
   - Physiological glucose range filtering (40-400 mg/dL)
   - Feature standardization

3. **Model Training:**
   - Supports three model types:
     - Linear Regression (for Arduino deployment)
     - Random Forest (for performance comparison)
     - Gradient Boosting (for best accuracy)
   - Automatic hyperparameter tuning

4. **Evaluation Metrics:**
   - Mean Absolute Error (MAE)
   - Root Mean Squared Error (RMSE)
   - R² Score
   - Clinical accuracy percentages (within 15/20 mg/dL)
   - Clarke Error Grid analysis
   - Residual plots
   - Feature importance visualization

5. **Output:**
   - Arduino-compatible CSV coefficient files
   - C header file for direct inclusion in firmware
   - Visualizations (scatter plots, error grids)
   - Joblib format for tree-based models

### Usage Instructions:

1. **Install dependencies:**
```bash
pip install pandas numpy scikit-learn matplotlib seaborn joblib
```

2. **Run training:**
```bash
# For linear regression (default)
python train_model.py --data path/to/training_data.csv

# For random forest
python train_model.py --model random_forest --data data/training_directory/

# With custom options
python train_model.py --model gradient_boosting --test_size 0.15 --output my_models/
```

3. **Output Files:**
   - `clarke_grid_*.png`: Clinical accuracy visualization
   - `residuals_*.png`: Prediction error analysis
   - `feature_importance_*.png`: Feature ranking
   - `glucose_predictions_scatter.png`: Overall accuracy
   - `models/production/LinearRegression_coeff_*.csv`: Arduino-compatible coefficients
   - `models/production/model_coefficients.h`: C header file for firmware

### Sample Data Format (CSV):

| timestamp          | ratio   | variability | slope  | glucose |
|--------------------|---------|-------------|--------|---------|
| 1689291000000      | 1.2345  | 0.5678      | 12.345 | 98.7    |
| 1689291060000      | 1.1987  | 0.5892      | 11.876 | 102.4   |
| ...                | ...     | ...         | ...    | ...     |

### Clinical Validation:

The Clarke Error Grid analysis provides clinical relevance assessment:
- **Zone A:** Clinically accurate predictions
- **Zone B:** Acceptable errors (<20% deviation)
- **Other Zones:** Potentially dangerous mispredictions

### Next Steps for Deployment:

1. Copy generated `model_coefficients.h` to your Arduino project
2. Include in firmware:
```cpp
#include "model_coefficients.h"

float predict_glucose(float ratio, float variability, float slope) {
  return intercept + 
         ratio_coeff * ratio +
         var_coeff * variability +
         slope_coeff * slope;
}
```

3. For tree-based models:
   - Convert to TensorFlow Lite using ONNX
   - Deploy with TensorFlow Lite Micro

This script provides a complete pipeline from data to deployable model, with robust validation and clinical accuracy assessment.
