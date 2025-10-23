#!/usr/bin/env python3
"""
Development startup script for Rocket Fuel Optimizer.
"""
import subprocess
import sys
import time
import threading
import os


def start_backend():
    """Start the FastAPI backend."""
    print("🚀 Starting FastAPI backend...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.api:app", 
            "--reload", 
            "--port", "8000",
            "--host", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")


def start_frontend():
    """Start the Streamlit frontend."""
    print("🎨 Starting Streamlit frontend...")
    time.sleep(3)  # Wait for backend to start
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", 
            "run", "frontend/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")


def main():
    """Start both backend and frontend in parallel."""
    print("🚀 Starting Rocket Fuel Optimizer Development Environment")
    print("=" * 60)
    
    # Check if requirements are installed
    try:
        import fastapi
        import streamlit
        import pandas
        import sklearn
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")
        return
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down development environment...")
        print("✅ Goodbye!")


if __name__ == "__main__":
    main()