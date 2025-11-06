# Mereb gRPC

A gRPC-based CSV processing service with asynchronous processing using Celery, a FastAPI gateway, and React frontend.

## Description

This project provides a backend service for processing CSV files asynchronously with a React frontend. It consists of:

- A gRPC server that handles CSV processing logic with Celery for async tasks
- A FastAPI gateway that accepts file uploads and communicates with the gRPC server
- A React frontend for uploading and downloading CSV files
- Redis as message broker and result backend for Celery

## Architecture

The application follows a microservices architecture:

1. **Frontend (React + Vite)**: Provides the user interface for uploading CSV files and monitoring processing status.

2. **Gateway (FastAPI)**: Acts as an API gateway, handling HTTP requests from the frontend and communicating with the gRPC server using a global channel for performance.

3. **gRPC Server**: Handles the core CSV processing logic. Uses Celery to offload heavy processing tasks asynchronously.

4. **Celery Worker**: Processes CSV files in the background, storing results in Redis.

5. **Redis**: Serves as both the message broker for Celery tasks and the result backend for storing task states and results.

## Installation

Ensure you have Python 3.13+ and Redis installed. The project uses pyenv for Python version management (see `.python-version`).

Navigate to the backend directory and install dependencies using uv:

```bash
cd backend
uv sync
```

## Development Setup

### Code Quality

Format code using Black and isort:

```bash
cd backend
uv run black .
uv run isort .
```

Lint code using Ruff:

```bash
cd backend
uv run ruff check .
```

For the frontend:

```bash
cd frontend
npm run lint
```

### Testing

Run the test suite using uv:

```bash
cd backend
uv run pytest
```

This will execute all unit tests, including tests that use the sample CSV files in `backend/test/` to validate the CSV processing functionality.

## Frontend Installation

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

## Usage

1. Start Redis server:

```bash
redis-server
```

2. Start the Celery worker:

```bash
uv run celery -A backend.celery_app worker --loglevel=info
```

3. Start the gRPC server:

```bash
uv run backend/csv_processor_server.py
```

4. Start the FastAPI gateway:

```bash
uv run backend/main.py
```

The gateway will be available at http://localhost:8000 (configurable via FASTAPI_HOST and FASTAPI_PORT env vars).

5. Start the frontend:

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173 (default Vite port).

## API

### Upload CSV

POST /upload

Upload a CSV file. The service processes it asynchronously via gRPC and Celery, then returns a download URL, initial status, and task ID for the processed CSV.

### Check Processing Status

GET /status/{task_id}

Check the status of a CSV processing task. Returns completion status, processed CSV data, current status, and progress details including lines processed, departments, and time elapsed.

### Download Processed CSV

GET /download/{file_id}

Download the processed CSV file.

## Environment Variables

```env
GRPC_HOST=localhost          # Host for gRPC server
GRPC_PORT=50051              # Port for gRPC server
FASTAPI_HOST=0.0.0.0         # Host for FastAPI
FASTAPI_PORT=8000            # Port for FastAPI
RESULTS_DIR=results          # Directory for processed results
CELERY_BROKER_URL=redis://localhost:6379/0  # URL for Celery message broker
CELERY_RESULT_BACKEND=redis://localhost:6379/0  # URL for Celery result backend
```

## Dependencies

### Backend

- grpcio>=1.76.0
- grpcio-tools>=1.76.0
- fastapi
- python-multipart>=0.0.20
- uvicorn
- black>=25.9.0
- python-dotenv
- celery
- redis
- ipdb>=0.13.13
- isort>=7.0.0
- pytest
- ruff>=0.14.3

### Frontend

- react ^19.1.1
- react-dom ^19.1.1

#### Dev Dependencies

- @eslint/js ^9.36.0
- @types/react ^19.1.16
- @types/react-dom ^19.1.9
- @vitejs/plugin-react ^5.0.4
- eslint ^9.36.0
- eslint-plugin-react-hooks ^5.2.0
- eslint-plugin-react-refresh ^0.4.22
- globals ^16.4.0
- vite ^7.1.7
