"""
Core rocket fuel optimization engine with pure functions.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from scipy.optimize import minimize


def generate_data(seed: int = 42, size: int = 500) -> pd.DataFrame:
    """Generate synthetic rocket fuel data.
    
    Args:
        seed: Random seed for reproducibility
        size: Number of data points to generate
        
    Returns:
        DataFrame with rocket fuel parameters and thrust values
    """
    np.random.seed(seed)
    
    O_F_ratio = np.random.uniform(2, 6, size)
    chamber_pressure = np.random.uniform(1, 10, size)
    combustion_temp = np.random.uniform(2500, 4000, size)
    specific_impulse = np.random.uniform(200, 450, size)
    thrust = specific_impulse * chamber_pressure * 9.81 * 0.1
    
    return pd.DataFrame({
        'O/F Ratio': O_F_ratio,
        'Chamber Pressure (MPa)': chamber_pressure,
        'Combustion Temp (K)': combustion_temp,
        'Specific Impulse (ISP)': specific_impulse,
        'Thrust (kN)': thrust
    })


def simulate(params: Dict[str, float], model) -> Dict[str, Any]:
    """Simulate rocket performance with given parameters.
    
    Args:
        params: Dictionary with O_F_ratio, pressure, temp, isp
        model: Trained ML model for prediction
        
    Returns:
        Dictionary with simulation results
    """
    df_input = pd.DataFrame({
        'O/F Ratio': [params['O_F_ratio']],
        'Chamber Pressure (MPa)': [params['pressure']],
        'Combustion Temp (K)': [params['temp']],
        'Specific Impulse (ISP)': [params['isp']]
    })
    
    predicted_thrust = model.predict(df_input)[0]
    
    return {
        'thrust': float(predicted_thrust),
        'efficiency': float(predicted_thrust / (params['pressure'] * params['isp'])),
        'temperature_ratio': float(params['temp'] / 3000),  # Normalized to typical temp
        'params': params
    }


def optimize_fuel_mixture(model, alpha: float = 0.5, max_temp: float = 4000) -> Dict[str, Any]:
    """Optimize fuel mixture using multi-objective optimization.
    
    Args:
        model: Trained ML model
        alpha: Weight for thrust vs temperature (0-1)
        max_temp: Maximum temperature constraint
        
    Returns:
        Dictionary with optimization results
    """
    def objective(params):
        O_F, p, T = params
        df_in = pd.DataFrame({
            'O/F Ratio': [O_F],
            'Chamber Pressure (MPa)': [p],
            'Combustion Temp (K)': [T],
            'Specific Impulse (ISP)': [300]
        })
        pred_thrust = model.predict(df_in)[0]
        return alpha * (-pred_thrust) + (1 - alpha) * T

    constraints = [
        {'type': 'ineq', 'fun': lambda x: max_temp - x[2]}
    ]
    bounds = [(2, 6), (1, 10), (2500, 5000)]
    initial_guess = [3.5, 5.0, 3000.0]

    result = minimize(objective, initial_guess, bounds=bounds, constraints=constraints)
    
    if result.success:
        optimal_params = {
            'O_F_ratio': float(result.x[0]),
            'pressure': float(result.x[1]),
            'temp': float(result.x[2]),
            'isp': 300.0
        }
        
        simulation_result = simulate(optimal_params, model)
        
        return {
            'success': True,
            'optimal_params': optimal_params,
            'predicted_thrust': simulation_result['thrust'],
            'optimization_value': float(result.fun)
        }
    else:
        return {
            'success': False,
            'error': result.message
        }


def compute_metrics(data: pd.DataFrame, predictions: np.ndarray, actuals: np.ndarray) -> Dict[str, float]:
    """Compute performance metrics for model evaluation.
    
    Args:
        data: Input DataFrame
        predictions: Model predictions
        actuals: Actual values
        
    Returns:
        Dictionary with computed metrics
    """
    from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
    
    mae = mean_absolute_error(actuals, predictions)
    r2 = r2_score(actuals, predictions)
    rmse = np.sqrt(mean_squared_error(actuals, predictions))
    
    return {
        'mae': float(mae),
        'r2': float(r2),
        'rmse': float(rmse),
        'data_points': len(data)
    }