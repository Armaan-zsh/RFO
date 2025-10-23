"""
FastAPI backend for rocket fuel optimization.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import json
from datetime import datetime
from pathlib import Path

from .engine import generate_data, simulate, optimize_fuel_mixture, compute_metrics
from .models import train_model, save_model, load_model
from .worker import JobQueue
from .database import get_db, Experiment, Result

app = FastAPI(title="Rocket Fuel Optimizer API", version="1.0.0")

# Global job queue
job_queue = JobQueue()

# Global model cache
_model_cache = {}


class ExperimentParams(BaseModel):
    """Parameters for rocket fuel experiment."""
    O_F_ratio: float = Field(ge=2.0, le=6.0, description="Oxidizer to Fuel ratio")
    pressure: float = Field(ge=1.0, le=10.0, description="Chamber pressure in MPa")
    temp: float = Field(ge=2500.0, le=5000.0, description="Combustion temperature in K")
    isp: float = Field(ge=200.0, le=450.0, description="Specific impulse")
    alpha: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Optimization weight")
    max_temp: Optional[float] = Field(default=4000.0, description="Max temperature constraint")
    tune_model: Optional[bool] = Field(default=False, description="Enable hyperparameter tuning")


class JobResponse(BaseModel):
    """Response for job submission."""
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    """Job status response."""
    job_id: str
    status: str
    progress: float
    message: str
    created_at: datetime


class JobResult(BaseModel):
    """Job result response."""
    job_id: str
    status: str
    results: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


def get_or_train_model():
    """Get cached model or train a new one."""
    if 'default' not in _model_cache:
        # Generate training data and train model
        df = generate_data(seed=42, size=500)
        model, metrics = train_model(df, tune_hyperparams=False)
        _model_cache['default'] = {'model': model, 'metrics': metrics}
    
    return _model_cache['default']['model']


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Rocket Fuel Optimizer API", "status": "running"}


@app.post("/run", response_model=JobResponse)
async def run_experiment(params: ExperimentParams, background_tasks: BackgroundTasks):
    """Submit a rocket fuel optimization experiment."""
    job_id = str(uuid.uuid4())
    
    # Store experiment in database
    db = next(get_db())
    experiment = Experiment(
        id=job_id,
        params=params.dict(),
        status="queued"
    )
    db.add(experiment)
    db.commit()
    
    # Queue the job
    job_queue.enqueue_job(job_id, _run_experiment_task, params.dict())
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        message="Experiment queued successfully"
    )


@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get status of a running job."""
    db = next(get_db())
    experiment = db.query(Experiment).filter(Experiment.id == job_id).first()
    
    if not experiment:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_status = job_queue.get_job_status(job_id)
    
    return JobStatus(
        job_id=job_id,
        status=job_status['status'],
        progress=job_status['progress'],
        message=job_status['message'],
        created_at=experiment.created_at
    )


@app.get("/result/{job_id}", response_model=JobResult)
async def get_job_result(job_id: str):
    """Get results of a completed job."""
    db = next(get_db())
    result = db.query(Result).filter(Result.experiment_id == job_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    experiment = db.query(Experiment).filter(Experiment.id == job_id).first()
    
    return JobResult(
        job_id=job_id,
        status=result.status,
        results=result.data if result.status == "completed" else None,
        error=result.error_message if result.status == "failed" else None,
        created_at=experiment.created_at,
        completed_at=result.completed_at
    )


def _run_experiment_task(job_id: str, params: Dict[str, Any]):
    """Background task to run experiment."""
    db = next(get_db())
    
    try:
        # Update status to running
        job_queue.update_job_status(job_id, "running", 0.1, "Starting experiment")
        
        # Get or train model
        model = get_or_train_model()
        job_queue.update_job_status(job_id, "running", 0.3, "Model loaded")
        
        # Run simulation
        sim_params = {
            'O_F_ratio': params['O_F_ratio'],
            'pressure': params['pressure'],
            'temp': params['temp'],
            'isp': params['isp']
        }
        simulation_result = simulate(sim_params, model)
        job_queue.update_job_status(job_id, "running", 0.6, "Simulation completed")
        
        # Run optimization if requested
        optimization_result = None
        if params.get('alpha') is not None:
            optimization_result = optimize_fuel_mixture(
                model, 
                alpha=params['alpha'], 
                max_temp=params.get('max_temp', 4000)
            )
        job_queue.update_job_status(job_id, "running", 0.9, "Optimization completed")
        
        # Prepare results
        results = {
            'simulation': simulation_result,
            'optimization': optimization_result,
            'model_metrics': _model_cache['default']['metrics']
        }
        
        # Store results in database
        result = Result(
            experiment_id=job_id,
            status="completed",
            data=results,
            completed_at=datetime.utcnow()
        )
        db.add(result)
        
        # Update experiment status
        experiment = db.query(Experiment).filter(Experiment.id == job_id).first()
        experiment.status = "completed"
        
        db.commit()
        job_queue.update_job_status(job_id, "completed", 1.0, "Experiment completed successfully")
        
    except Exception as e:
        # Handle errors
        error_msg = str(e)
        
        result = Result(
            experiment_id=job_id,
            status="failed",
            error_message=error_msg,
            completed_at=datetime.utcnow()
        )
        db.add(result)
        
        experiment = db.query(Experiment).filter(Experiment.id == job_id).first()
        experiment.status = "failed"
        
        db.commit()
        job_queue.update_job_status(job_id, "failed", 0.0, f"Experiment failed: {error_msg}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)