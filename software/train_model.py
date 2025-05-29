"""
Machine Learning Model Trainer for Non-Invasive Glucose Monitoring
Author: Rasya Pratama (Raz Rizkov)

This script:
1. Loads and preprocesses PPG-glucose paired data
2. Trains a machine learning model (Linear Regression, Random Forest, or Gradient Boosting)
3. Evaluates model performance with multiple metrics
4. Visualizes results and feature importance
5. Saves model coefficients for Arduino deployment
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import joblib
import argparse
import os

# Configuration
plt.style.use('ggplot')
pd.set_option('display.max_columns', 10)
sns.set_palette('colorblind')

def load_data(data_path):
    """
    Load and preprocess training data from CSV files
    """
    if os.path.isdir(data_path):
        # Load all CSV files in directory
        files = [f for f in os.listdir(data_path) if f.endswith('.csv')]
        dfs = []
        for file in files:
            file_path = os.path.join(data_path, file)
            try:
                df = pd.read_csv(file_path)
                dfs.append(df)
                print(f"Loaded {file} with {len(df)} records")
            except Exception as e:
                print(f"Error loading {file}: {str(e)}")
        
        if not dfs:
            raise ValueError("No valid CSV files found in directory")
            
        data = pd.concat(dfs, ignore_index=True)
    else:
        # Load single file
        data = pd.read_csv(data_path)
        print(f"Loaded single file with {len(data)} records")
    
    # Check required columns
    required_cols = {'timestamp', 'ratio', 'variability', 'slope', 'glucose'}
    if not required_cols.issubset(data.columns):
        missing = required_cols - set(data.columns)
        raise ValueError(f"Missing required columns: {missing}")
    
    # Initial preprocessing
    data = data.drop_duplicates()
    data = data.dropna(subset=['glucose'])  # Must have glucose values
    
    print(f"\nRaw data summary ({len(data)} records):")
    print(data[['ratio', 'variability', 'slope', 'glucose']].describe().round(2))
    
    return data

def preprocess_data(data):
    """
    Clean and preprocess the dataset
    """
    # Handle missing values
    imputer = SimpleImputer(strategy='median')
    data[['ratio', 'variability', 'slope']] = imputer.fit_transform(
        data[['ratio', 'variability', 'slope']]
    )
    
    # Remove physiologically impossible glucose values
    data = data[(data['glucose'] >= 40) & (data['glucose'] <= 400)]
    
    # Calculate additional features
    data['pulse_rate'] = 60 / (data['variability'] + 1e-6)  # Approximate pulse rate
    data['acdc_ratio'] = data['variability'] / data['ratio']  # AC/DC component ratio
    
    # Remove outliers using IQR method
    def remove_outliers(df, columns, factor=1.5):
        for col in columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            df = df[(df[col] >= q1 - factor*iqr) & (df[col] <= q3 + factor*iqr)]
        return df
    
    data = remove_outliers(data, ['ratio', 'variability', 'slope', 'glucose'])
    
    print(f"\nProcessed data summary ({len(data)} records):")
    print(data[['ratio', 'variability', 'slope', 'glucose', 'pulse_rate', 'acdc_ratio']].describe().round(2))
    
    return data

def train_model(X_train, y_train, model_type='linear'):
    """
    Train specified regression model
    """
    print(f"\nTraining {model_type} model...")
    
    if model_type == 'linear':
        model = LinearRegression()
    elif model_type == 'random_forest':
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
    elif model_type == 'gradient_boosting':
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """
    Evaluate model performance and generate metrics
    """
    y_pred = model.predict(X_test)
    
    # Calculate evaluation metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Clarke Error Grid Analysis
    def clarke_error_grid(ref, pred, title):
        plt.figure(figsize=(10, 8))
        plt.scatter(ref, pred, alpha=0.5)
        plt.plot([0, 400], [0, 400], 'k--')
        plt.plot([0, 175/3], [70, 70], 'r-')  # Hypoglycemia threshold
        plt.plot([70, 70], [0, 180], 'r-')    # Hypoglycemia threshold
        plt.plot([180, 400], [180, 180], 'r-') # Hyperglycemia threshold
        plt.plot([180, 180], [0, 400], 'r-')   # Hyperglycemia threshold
        
        # Add zones
        plt.fill_between([0, 70], 0, 70, color='green', alpha=0.1)  # Zone A
        plt.fill_between([70, 180], 70, 180, color='green', alpha=0.1)
        plt.fill_between([180, 400], 180, 400, color='green', alpha=0.1)
        plt.fill_between([0, 70], 70, 180, color='yellow', alpha=0.1)  # Zone B
        plt.fill_between([70, 180], 0, 70, color='yellow', alpha=0.1)
        plt.fill_between([70, 180], 180, 400, color='yellow', alpha=0.1)
        plt.fill_between([180, 400], 0, 180, color='yellow', alpha=0.1)
        
        plt.title(f'Clarke Error Grid: {title}')
        plt.xlabel('Reference Glucose (mg/dL)')
        plt.ylabel('Predicted Glucose (mg/dL)')
        plt.grid(True)
        plt.savefig(f'clarke_grid_{title}.png', dpi=300)
        plt.close()
    
    clarke_error_grid(y_test, y_pred, model.__class__.__name__)
    
    # Residual plot
    residuals = y_test - y_pred
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=y_pred, y=residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='-')
    plt.title('Residual Plot')
    plt.xlabel('Predicted Glucose (mg/dL)')
    plt.ylabel('Residuals')
    plt.savefig(f'residuals_{model.__class__.__name__}.png', dpi=300)
    plt.close()
    
    # Feature importance
    if hasattr(model, 'feature_importances_'):
        plt.figure(figsize=(10, 6))
        features = X_test.columns
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        plt.title('Feature Importances')
        plt.bar(range(len(importances)), importances[indices], align='center')
        plt.xticks(range(len(importances)), [features[i] for i in indices], rotation=45)
        plt.tight_layout()
        plt.savefig(f'feature_importance_{model.__class__.__name__}.png', dpi=300)
        plt.close()
    
    return {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'predictions': y_pred,
        'actuals': y_test
    }

def save_coefficients(model, features, output_dir='models/production'):
    """
    Save model coefficients in Arduino-compatible format
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    model_name = model.__class__.__name__
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{model_name}_coeff_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    if isinstance(model, LinearRegression):
        coeffs = np.insert(model.coef_, 0, model.intercept_)
        feature_names = ['intercept'] + features.tolist()
        coeff_df = pd.DataFrame({
            'feature': feature_names,
            'coefficient': coeffs
        })
        coeff_df.to_csv(filepath, index=False)
        
        # Create Arduino-compatible header
        header_path = os.path.join(output_dir, f"model_coefficients.h")
        with open(header_path, 'w') as f:
            f.write("#ifndef MODEL_COEFFICIENTS_H\n")
            f.write("#define MODEL_COEFFICIENTS_H\n\n")
            for i, row in coeff_df.iterrows():
                f.write(f"const float {row['feature']} = {row['coefficient']:.6f};\n")
            f.write("\n#endif")
        
        print(f"\nSaved Arduino header to: {header_path}")
    
    elif isinstance(model, (RandomForestRegressor, GradientBoostingRegressor)):
        # Save model in joblib format for possible future use
        joblib.dump(model, os.path.join(output_dir, f"{model_name}_{timestamp}.joblib"))
        print("Tree-based models require TinyML conversion for Arduino deployment")
        print("Exported model in joblib format for reference")
    
    print(f"Saved coefficients to: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='Train Glucose Prediction Model')
    parser.add_argument('--data', type=str, default='data/training', 
                        help='Path to training data file or directory')
    parser.add_argument('--model', type=str, default='linear', 
                        choices=['linear', 'random_forest', 'gradient_boosting'],
                        help='Model type to train')
    parser.add_argument('--test_size', type=float, default=0.2,
                        help='Proportion of data for testing (0-1)')
    parser.add_argument('--output', type=str, default='models/production',
                        help='Output directory for model coefficients')
    args = parser.parse_args()
    
    # Load and preprocess data
    print("="*60)
    print("GLUCOSE PREDICTION MODEL TRAINING")
    print("="*60)
    data = load_data(args.data)
    processed_data = preprocess_data(data)
    
    # Prepare features and target
    features = processed_data[['ratio', 'variability', 'slope', 'pulse_rate', 'acdc_ratio']]
    target = processed_data['glucose']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=args.test_size, random_state=42
    )
    
    # Standardize features
    scaler = StandardScaler()
    X_train = pd.DataFrame(scaler.fit_transform(X_train), columns=features.columns)
    X_test = pd.DataFrame(scaler.transform(X_test), columns=features.columns)
    
    # Train model
    model = train_model(X_train, y_train, args.model)
    
    # Evaluate model
    results = evaluate_model(model, X_test, y_test)
    
    # Print evaluation results
    print("\n" + "="*60)
    print("MODEL EVALUATION RESULTS")
    print("="*60)
    print(f"MAE: {results['mae']:.2f} mg/dL")
    print(f"RMSE: {results['rmse']:.2f} mg/dL")
    print(f"R² Score: {results['r2']:.2f}")
    
    # Clinical accuracy assessment
    within_15 = np.mean(np.abs(results['actuals'] - results['predictions']) < 15
    within_20 = np.mean(np.abs(results['actuals'] - results['predictions']) < 20
    print(f"Clinical Accuracy (within 15 mg/dL): {within_15*100:.1f}%")
    print(f"Clinical Accuracy (within 20 mg/dL): {within_20*100:.1f}%")
    
    # Save coefficients
    save_coefficients(model, features.columns, args.output)
    
    # Final scatter plot
    plt.figure(figsize=(10, 8))
    plt.scatter(results['actuals'], results['predictions'], alpha=0.5)
    plt.plot([40, 400], [40, 400], 'r--')
    plt.title('Actual vs Predicted Glucose Levels')
    plt.xlabel('Reference Glucose (mg/dL)')
    plt.ylabel('Predicted Glucose (mg/dL)')
    plt.grid(True)
    plt.savefig('glucose_predictions_scatter.png', dpi=300)
    plt.close()
    
    print("\nTraining complete! Visualizations saved to current directory")

if __name__ == "__main__":
    main()
