"""
Machine learning model management for rocket fuel optimization.
"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_absolute_error, r2_score


def train_model(df: pd.DataFrame, tune_hyperparams: bool = False) -> Tuple[Any, Dict[str, float]]:
    """Train a machine learning model on rocket fuel data.
    
    Args:
        df: DataFrame with rocket fuel parameters and thrust
        tune_hyperparams: Whether to perform hyperparameter tuning
        
    Returns:
        Tuple of (trained_model, metrics_dict)
    """
    # Prepare features and target
    X = df[['O/F Ratio', 'Chamber Pressure (MPa)', 'Combustion Temp (K)', 'Specific Impulse (ISP)']]
    y = df['Thrust (kN)']
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if tune_hyperparams:
        # Hyperparameter tuning
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [None, 10],
            'min_samples_split': [2, 5]
        }
        
        base_model = RandomForestRegressor(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            cv=3,
            scoring='neg_mean_absolute_error',
            n_jobs=-1
        )
        grid_search.fit(X_train, y_train)
        model = grid_search.best_estimator_
        best_params = grid_search.best_params_
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        best_params = {}
    
    # Evaluate model
    y_pred = model.predict(X_test)
    metrics = {
        'mae': float(mean_absolute_error(y_test, y_pred)),
        'r2': float(r2_score(y_test, y_pred)),
        'train_size': len(X_train),
        'test_size': len(X_test)
    }
    
    if tune_hyperparams:
        metrics['best_params'] = best_params
    
    return model, metrics


def predict(model: Any, X: pd.DataFrame) -> np.ndarray:
    """Make predictions using trained model.
    
    Args:
        model: Trained ML model
        X: Input features DataFrame
        
    Returns:
        Array of predictions
    """
    return model.predict(X)


def save_model(model: Any, path: str) -> bool:
    """Save trained model to disk.
    
    Args:
        model: Trained ML model
        path: File path to save model
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(model, f)
        return True
    except Exception as e:
        print(f"Error saving model: {e}")
        return False


def load_model(path: str) -> Optional[Any]:
    """Load trained model from disk.
    
    Args:
        path: File path to load model from
        
    Returns:
        Loaded model or None if failed
    """
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None


def validate_input_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validate input data format and content.
    
    Args:
        df: Input DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_cols = ['O/F Ratio', 'Chamber Pressure (MPa)', 'Combustion Temp (K)', 
                     'Specific Impulse (ISP)', 'Thrust (kN)']
    
    # Check required columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        return False, f"Missing required columns: {missing_cols}"
    
    # Check for reasonable value ranges
    if df['O/F Ratio'].min() < 1 or df['O/F Ratio'].max() > 10:
        return False, "O/F Ratio values out of reasonable range (1-10)"
    
    if df['Chamber Pressure (MPa)'].min() < 0.1 or df['Chamber Pressure (MPa)'].max() > 20:
        return False, "Chamber Pressure values out of reasonable range (0.1-20 MPa)"
    
    if df['Combustion Temp (K)'].min() < 1000 or df['Combustion Temp (K)'].max() > 6000:
        return False, "Combustion Temperature values out of reasonable range (1000-6000 K)"
    
    return True, ""