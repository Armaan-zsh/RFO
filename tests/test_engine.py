"""
Unit tests for rocket fuel optimization engine.
"""
import pytest
import pandas as pd
import numpy as np
from backend.engine import generate_data, simulate, compute_metrics, optimize_fuel_mixture
from backend.models import train_model


class TestEngine:
    """Test cases for engine functions."""
    
    def test_generate_data(self):
        """Test synthetic data generation."""
        df = generate_data(seed=42, size=100)
        
        assert len(df) == 100
        assert all(col in df.columns for col in [
            'O/F Ratio', 'Chamber Pressure (MPa)', 'Combustion Temp (K)', 
            'Specific Impulse (ISP)', 'Thrust (kN)'
        ])
        
        # Check value ranges
        assert df['O/F Ratio'].min() >= 2.0
        assert df['O/F Ratio'].max() <= 6.0
        assert df['Chamber Pressure (MPa)'].min() >= 1.0
        assert df['Chamber Pressure (MPa)'].max() <= 10.0
    
    def test_generate_data_reproducible(self):
        """Test that data generation is reproducible with same seed."""
        df1 = generate_data(seed=42, size=50)
        df2 = generate_data(seed=42, size=50)
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_simulate(self):
        """Test simulation function."""
        # Generate test data and train model
        df = generate_data(seed=42, size=100)
        model, _ = train_model(df)
        
        params = {
            'O_F_ratio': 3.5,
            'pressure': 5.0,
            'temp': 3000.0,
            'isp': 300.0
        }
        
        result = simulate(params, model)
        
        assert 'thrust' in result
        assert 'efficiency' in result
        assert 'temperature_ratio' in result
        assert 'params' in result
        assert isinstance(result['thrust'], float)
        assert result['thrust'] > 0
    
    def test_compute_metrics(self):
        """Test metrics computation."""
        # Create test data
        df = pd.DataFrame({'test': [1, 2, 3]})
        predictions = np.array([1.1, 2.1, 2.9])
        actuals = np.array([1.0, 2.0, 3.0])
        
        metrics = compute_metrics(df, predictions, actuals)
        
        assert 'mae' in metrics
        assert 'r2' in metrics
        assert 'rmse' in metrics
        assert 'data_points' in metrics
        assert metrics['data_points'] == 3
        assert 0 <= metrics['r2'] <= 1
        assert metrics['mae'] >= 0
    
    def test_optimize_fuel_mixture(self):
        """Test fuel mixture optimization."""
        # Generate test data and train model
        df = generate_data(seed=42, size=200)
        model, _ = train_model(df)
        
        result = optimize_fuel_mixture(model, alpha=0.5, max_temp=4000)
        
        assert 'success' in result
        if result['success']:
            assert 'optimal_params' in result
            assert 'predicted_thrust' in result
            
            params = result['optimal_params']
            assert 2.0 <= params['O_F_ratio'] <= 6.0
            assert 1.0 <= params['pressure'] <= 10.0
            assert params['temp'] <= 4000  # Constraint check
            assert result['predicted_thrust'] > 0