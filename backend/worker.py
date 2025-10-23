"""
Lightweight job queue implementation for rocket fuel optimization.
"""
import threading
import time
from typing import Dict, Any, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import queue


class JobQueue:
    """Simple in-memory job queue using ThreadPoolExecutor."""
    
    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def enqueue_job(self, job_id: str, func: Callable, *args, **kwargs):
        """Enqueue a job for background execution."""
        with self.lock:
            self.jobs[job_id] = {
                'status': 'queued',
                'progress': 0.0,
                'message': 'Job queued',
                'created_at': datetime.utcnow(),
                'future': None
            }
        
        # Submit job to executor
        future = self.executor.submit(func, job_id, *args, **kwargs)
        
        with self.lock:
            self.jobs[job_id]['future'] = future
            self.jobs[job_id]['status'] = 'running'
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get current status of a job."""
        with self.lock:
            if job_id not in self.jobs:
                return {
                    'status': 'not_found',
                    'progress': 0.0,
                    'message': 'Job not found'
                }
            
            job = self.jobs[job_id]
            
            # Check if job is done
            if job['future'] and job['future'].done():
                if job['status'] not in ['completed', 'failed']:
                    try:
                        job['future'].result()  # This will raise exception if job failed
                        if job['status'] != 'failed':  # Don't override failed status
                            job['status'] = 'completed'
                            job['progress'] = 1.0
                            job['message'] = 'Job completed'
                    except Exception as e:
                        job['status'] = 'failed'
                        job['progress'] = 0.0
                        job['message'] = f'Job failed: {str(e)}'
            
            return {
                'status': job['status'],
                'progress': job['progress'],
                'message': job['message']
            }
    
    def update_job_status(self, job_id: str, status: str, progress: float, message: str):
        """Update job status (called from within job execution)."""
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id]['status'] = status
                self.jobs[job_id]['progress'] = progress
                self.jobs[job_id]['message'] = message
    
    def cleanup_completed_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs."""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        with self.lock:
            jobs_to_remove = []
            for job_id, job in self.jobs.items():
                if (job['status'] in ['completed', 'failed'] and 
                    job['created_at'].timestamp() < cutoff_time):
                    jobs_to_remove.append(job_id)
            
            for job_id in jobs_to_remove:
                del self.jobs[job_id]
    
    def shutdown(self):
        """Shutdown the job queue."""
        self.executor.shutdown(wait=True)