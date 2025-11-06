# Mereb gRPC

A gRPC-based CSV processing service with asynchronous processing using Celery, a FastAPI gateway, and React frontend.

## Description

This project provides a backend service for processing CSV files asynchronously with a React frontend. It consists of:

- A gRPC server that handles CSV processing logic with Celery for async tasks
- A FastAPI gateway that accepts file uploads and communicates with the gRPC server
- A React frontend for uploading and downloading CSV files
- Redis as message broker and result backend for Celery

## Installation

Ensure you have Python 3.13+ and Redis installed.

Navigate to the backend directory and install dependencies using uv:

```bash
cd backend
uv sync
```

## Testing

Run the test suite using uv:

```bash
cd backend
uv run pytest backend/
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
UPLOAD_DIR=uploads           # Directory for uploads
CELERY_BROKER_URL=redis://localhost:6379/0  # URL for Celery message broker
CELERY_RESULT_BACKEND=redis://localhost:6379/0  # URL for Celery result backend
```

## Dependencies

- grpcio
- grpcio-tools
- fastapi
- python-multipart
- uvicorn
- black
- python-dotenv
- celery
- redis
