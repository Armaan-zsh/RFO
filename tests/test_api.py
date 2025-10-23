"""
API tests for rocket fuel optimization.
"""
import pytest
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)


class TestAPI:
    """Test cases for API endpoints."""
    
    def test_root_endpoint(self):
        """Test root health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Rocket Fuel Optimizer API"
        assert data["status"] == "running"
    
    def test_run_experiment(self):
        """Test experiment submission endpoint."""
        params = {
            "O_F_ratio": 3.5,
            "pressure": 5.0,
            "temp": 3000.0,
            "isp": 300.0,
            "alpha": 0.5,
            "max_temp": 4000.0,
            "tune_model": False
        }
        
        response = client.post("/run", json=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
        assert "message" in data
    
    def test_run_experiment_validation(self):
        """Test parameter validation."""
        # Test invalid O/F ratio
        params = {
            "O_F_ratio": 10.0,  # Too high
            "pressure": 5.0,
            "temp": 3000.0,
            "isp": 300.0
        }
        
        response = client.post("/run", json=params)
        assert response.status_code == 422  # Validation error
    
    def test_status_endpoint_not_found(self):
        """Test status endpoint with non-existent job."""
        response = client.get("/status/non-existent-job-id")
        assert response.status_code == 404
    
    def test_result_endpoint_not_found(self):
        """Test result endpoint with non-existent job."""
        response = client.get("/result/non-existent-job-id")
        assert response.status_code == 404
    
    def test_experiment_workflow(self):
        """Test complete experiment workflow."""
        # Submit experiment
        params = {
            "O_F_ratio": 3.5,
            "pressure": 5.0,
            "temp": 3000.0,
            "isp": 300.0
        }
        
        response = client.post("/run", json=params)
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Check status (should be queued or running)
        response = client.get(f"/status/{job_id}")
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["job_id"] == job_id
        assert status_data["status"] in ["queued", "running", "completed"]
        
        # Wait a bit and check if job completes (in real scenario)
        # For testing, we'll just verify the endpoint structure
        import time
        time.sleep(2)
        
        response = client.get(f"/status/{job_id}")
        assert response.status_code == 200