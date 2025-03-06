#!/usr/bin/env python3
"""
Script to train a car price prediction model.
This script loads the dataset, preprocesses it, trains a model, and saves the model.
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

# Add the project root to the path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Import our preprocessing module
from data.preprocessing import CarDataPreprocessor

def train_model(model_type='linear', tune_hyperparams=False, show_plots=False):
    """
    Train a car price prediction model
    
    Args:
        model_type (str): Type of model to train ('linear', 'ridge', 'lasso', 'rf', 'gbm')
        tune_hyperparams (bool): Whether to tune hyperparameters using GridSearchCV
        show_plots (bool): Whether to show performance plots
        
    Returns:
        tuple: (model, test_score, feature_importances)
    """
    # Create directories
    models_dir = project_root / "api" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Load and preprocess data
    preprocessor = CarDataPreprocessor()
    df = preprocessor.load_data()
    processed_df = preprocessor.preprocess(df)
    
    # Print dataset information
    print(f"\nDataset shape after preprocessing: {processed_df.shape}")
    
    # Split the dataset
    print("\nSplitting data into train and test sets...")
    X = processed_df.drop(['price', 'CarName', 'model', 'symboling', 'car_ID', 'price_per_hp'], axis=1, errors='ignore')
    y = processed_df['price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training set size: {X_train.shape[0]} samples")
    print(f"Test set size: {X_test.shape[0]} samples")
    print(f"Number of features: {X_train.shape[1]}")
    
    # Select and train the model
    print(f"\nTraining {model_type} model...")
    
    if model_type == 'linear':
        model = LinearRegression()
        params = {}
    elif model_type == 'ridge':
        model = Ridge()
        params = {'alpha': [0.01, 0.1, 1.0, 10.0, 100.0]}
    elif model_type == 'lasso':
        model = Lasso()
        params = {'alpha': [0.001, 0.01, 0.1, 1.0, 10.0]}
    elif model_type == 'rf':
        model = RandomForestRegressor(random_state=42)
        params = {
            'n_estimators': [50, 100, 200],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10]
        }
    elif model_type == 'gbm':
        model = GradientBoostingRegressor(random_state=42)
        params = {
            'n_estimators': [50, 100, 200],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7]
        }
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Tune hyperparameters if requested
    if tune_hyperparams and params:
        print("Tuning hyperparameters...")
        grid_search = GridSearchCV(model, params, cv=5, scoring='r2', n_jobs=-1)
        grid_search.fit(X_train, y_train)
        model = grid_search.best_estimator_
        print(f"Best parameters: {grid_search.best_params_}")
    else:
        model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    print("\nModel Performance:")
    print(f"R² Score: {r2:.4f}")
    print(f"RMSE: ${rmse:.2f}")
    print(f"MAE: ${mae:.2f}")
    
    # Get feature importances if available
    feature_importances = {}
    if hasattr(model, 'feature_importances_'):
        # For tree-based models
        importances = model.feature_importances_
        feature_importances = dict(zip(X.columns, importances))
        
        # Display top 10 features
        print("\nTop 10 important features:")
        sorted_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10]
        for feature, importance in sorted_features:
            print(f"- {feature}: {importance:.4f}")
            
    elif hasattr(model, 'coef_'):
        # For linear models
        importances = np.abs(model.coef_)
        feature_importances = dict(zip(X.columns, importances))
        
        # Display top 10 features
        print("\nTop 10 features by coefficient magnitude:")
        sorted_features = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10]
        for feature, importance in sorted_features:
            print(f"- {feature}: {importance:.4f}")
    
    # Visualize results if requested
    if show_plots:
        # Create visualizations directory
        viz_dir = project_root / "notebooks" / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot actual vs. predicted
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
        plt.xlabel('Actual Price ($)')
        plt.ylabel('Predicted Price ($)')
        plt.title('Actual vs. Predicted Car Prices')
        plt.savefig(viz_dir / f"{model_type}_actual_vs_predicted.png")
        
        # Plot feature importance if available
        if feature_importances:
            plt.figure(figsize=(12, 8))
            importances_df = pd.DataFrame({
                'Feature': list(feature_importances.keys()),
                'Importance': list(feature_importances.values())
            }).sort_values('Importance', ascending=False).head(15)
            
            sns.barplot(x='Importance', y='Feature', data=importances_df)
            plt.title(f'Top 15 Feature Importance - {model_type.upper()}')
            plt.tight_layout()
            plt.savefig(viz_dir / f"{model_type}_feature_importance.png")
        
        # Plot residuals
        plt.figure(figsize=(10, 6))
        residuals = y_test - y_pred
        plt.scatter(y_pred, residuals, alpha=0.5)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.xlabel('Predicted Price ($)')
        plt.ylabel('Residuals ($)')
        plt.title('Residual Plot')
        plt.savefig(viz_dir / f"{model_type}_residuals.png")
        
        if show_plots:
            plt.show()
    
    # Save the model
    model_filename = f"car_price_{model_type}.pkl"
    joblib.dump(model, models_dir / model_filename)
    print(f"\nModel saved as {model_filename}")
    
    # Save model metadata
    model_info = {
        'model_type': model_type,
        'r2_score': r2,
        'rmse': rmse,
        'mae': mae,
        'num_features': X.shape[1],
        'feature_names': list(X.columns),
        'top_features': sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)[:10] if feature_importances else []
    }
    joblib.dump(model_info, models_dir / f"model_info_{model_type}.pkl")
    
    return model, r2, feature_importances

def run_all_models():
    """Run training for all model types and compare results"""
    results = {}
    model_types = ['linear', 'ridge', 'lasso', 'rf', 'gbm']
    
    for model_type in model_types:
        print(f"\n{'='*50}")
        print(f"Training {model_type.upper()} model")
        print(f"{'='*50}")
        
        _, r2, _ = train_model(model_type=model_type, tune_hyperparams=True)
        results[model_type] = r2
    
    # Print comparison
    print("\nModel Comparison:")
    print("="*50)
    for model_type, r2 in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"{model_type.upper()}: R² = {r2:.4f}")
    
    best_model = max(results.items(), key=lambda x: x[1])[0]
    print(f"\nBest model: {best_model.upper()} with R² = {results[best_model]:.4f}")
    
    # Create a symlink to the best model
    models_dir = project_root / "api" / "models"
    best_model_path = models_dir / f"car_price_{best_model}.pkl"
    default_model_path = models_dir / "car_price_model.pkl"
    
    if default_model_path.exists():
        default_model_path.unlink()
    
    # Create a copy (not symlink to ensure compatibility)
    import shutil
    shutil.copy2(best_model_path, default_model_path)
    print(f"Created default model link to {best_model_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train car price prediction models")
    parser.add_argument('--model', '-m', choices=['linear', 'ridge', 'lasso', 'rf', 'gbm', 'all'], 
                        default='linear', help='Model type to train')
    parser.add_argument('--tune', '-t', action='store_true', help='Tune hyperparameters')
    parser.add_argument('--plot', '-p', action='store_true', help='Show performance plots')
    
    args = parser.parse_args()
    
    if args.model == 'all':
        run_all_models()
    else:
        train_model(model_type=args.model, tune_hyperparams=args.tune, show_plots=args.plot)