#!/usr/bin/env python3
"""
Migration script to help transition from prototype app.py to modular structure.
"""
import shutil
import os
from pathlib import Path


def migrate_prototype():
    """Migrate from prototype to modular structure."""
    print("Migrating Rocket Fuel Optimizer to modular structure...")
    
    # Backup original app.py
    if os.path.exists("app.py"):
        print("Backing up original app.py...")
        shutil.copy("app.py", "app_prototype_backup.py")
        print("Backup created: app_prototype_backup.py")
    
    # Create data and models directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    print("Created data and models directories")
    
    # Create .env file template
    env_content = """# Environment Configuration
DATABASE_URL=sqlite:///./rocket_optimizer.db
API_BASE_URL=http://localhost:8000

# Optional: For production deployment
# DATABASE_URL=postgresql://user:password@localhost/rocket_optimizer
# REDIS_URL=redis://localhost:6379
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    print("Created .env configuration file")
    
    # Create .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite3

# Logs
*.log

# Environment
.env
.env.local

# Docker
.dockerignore

# Models and Data
models/*.pkl
data/*.csv
data/*.json

# OS
.DS_Store
Thumbs.db
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    print("Created .gitignore file")
    
    print("\nMigration completed successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start backend: uvicorn backend.api:app --reload")
    print("3. Start frontend: streamlit run frontend/streamlit_app.py")
    print("4. Or use Docker: docker-compose up --build")
    print("\nAccess points:")
    print("- Frontend: http://localhost:8501")
    print("- API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    migrate_prototype()