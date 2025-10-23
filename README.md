# 🚀 Rocket Fuel Optimizer

A production-ready web application for rocket fuel mixture optimization using machine learning and physics-based simulation.

## Features

- **Interactive Web Interface**: Streamlit frontend for experiment configuration and visualization
- **RESTful API**: FastAPI backend with asynchronous job processing
- **Machine Learning**: Scikit-learn models for thrust prediction and optimization
- **Job Queue**: Background processing for compute-intensive experiments
- **Data Persistence**: SQLAlchemy with SQLite/PostgreSQL support
- **Containerized**: Docker and docker-compose for easy deployment
- **Testing**: Comprehensive test suite with pytest
- **CI/CD**: GitHub Actions workflow for automated testing

## Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (optional)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd rocket-fuel-optimizer
   pip install -r requirements.txt
   ```

2. **Start the backend**:
   ```bash
   uvicorn backend.api:app --reload --port 8000
   ```

3. **Start the frontend** (in another terminal):
   ```bash
   streamlit run frontend/streamlit_app.py --server.port 8501
   ```

4. **Access the application**:
   - Frontend: http://localhost:8501
   - API docs: http://localhost:8000/docs

### Docker Deployment

1. **Start all services**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

## Architecture

```
├── backend/
│   ├── api.py          # FastAPI application
│   ├── engine.py       # Core business logic
│   ├── models.py       # ML model management
│   ├── worker.py       # Job queue implementation
│   ├── database.py     # Database models
│   └── explain.py      # AI explanations
├── frontend/
│   └── streamlit_app.py # Streamlit UI
├── tests/              # Test suite
├── Dockerfile          # Container definition
└── docker-compose.yml  # Multi-service orchestration
```

## API Endpoints

- `POST /run` - Submit experiment with parameters
- `GET /status/{job_id}` - Check job status and progress
- `GET /result/{job_id}` - Retrieve completed results

## Usage Example

```python
import requests

# Submit experiment
params = {
    "O_F_ratio": 3.5,
    "pressure": 5.0,
    "temp": 3000.0,
    "isp": 300.0,
    "alpha": 0.5,
    "max_temp": 4000.0
}

response = requests.post("http://localhost:8000/run", json=params)
job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8000/status/{job_id}")
print(status.json())

# Get results (when completed)
results = requests.get(f"http://localhost:8000/result/{job_id}")
print(results.json())
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend tests/

# Run specific test file
pytest tests/test_engine.py -v
```

## Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string (default: SQLite)
- `API_BASE_URL`: Backend API URL for frontend (default: http://localhost:8000)

### Database Setup

The application uses SQLite by default. For production, set:

```bash
export DATABASE_URL="postgresql://user:password@localhost/rocket_optimizer"
```

## Development

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting  
- **flake8** for linting

```bash
# Format code
black .
isort .

# Check linting
flake8 .
```

### Adding New Features

1. Add business logic to `backend/engine.py`
2. Update API endpoints in `backend/api.py`
3. Add tests in `tests/`
4. Update frontend in `frontend/streamlit_app.py`

## Troubleshooting

### Common Issues

1. **API Connection Error**: Ensure backend is running on port 8000
2. **Database Errors**: Check DATABASE_URL and permissions
3. **Docker Issues**: Ensure Docker daemon is running

### Logs

```bash
# View backend logs
docker-compose logs backend

# View frontend logs  
docker-compose logs frontend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.