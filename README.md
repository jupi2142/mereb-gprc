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
celery -A backend.celery_app worker --loglevel=info
```

3. Start the gRPC server:

```bash
python backend/csv_processor_server.py
```

4. Start the FastAPI gateway:

```bash
python backend/main.py
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

Upload a CSV file. The service processes it asynchronously via gRPC and Celery, then returns a download URL for the processed CSV.

### Download Processed CSV

GET /download/{file_id}

Download the processed CSV file.

## Environment Variables

- GRPC_HOST: Host for gRPC server (default: localhost)
- GRPC_PORT: Port for gRPC server (default: 50051)
- FASTAPI_HOST: Host for FastAPI (default: 0.0.0.0)
- FASTAPI_PORT: Port for FastAPI (default: 8000)
- UPLOAD_DIR: Directory for uploads (default: uploads)
- CELERY_BROKER_URL: URL for Celery message broker (default: redis://localhost:6379/0)
- CELERY_RESULT_BACKEND: URL for Celery result backend (default: redis://localhost:6379/0)

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
