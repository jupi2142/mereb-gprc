# Mereb gRPC

A gRPC-based CSV processing service with a FastAPI gateway and React frontend.

## Description

This project provides a backend service for processing CSV files with a React frontend. It consists of:

- A gRPC server that handles CSV processing logic
- A FastAPI gateway that accepts file uploads and communicates with the gRPC server
- A React frontend for uploading and downloading CSV files

## Installation

Ensure you have Python 3.13+ installed.

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

1. Start the gRPC server:

```bash
python backend/csv_processor_server.py
```

2. Start the FastAPI gateway:

```bash
python backend/main.py
```

The gateway will be available at http://localhost:8000 (configurable via FASTAPI_HOST and FASTAPI_PORT env vars).

3. Start the frontend:

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173 (default Vite port).

## API

### Upload CSV

POST /upload

Upload a CSV file. The service processes it via gRPC and returns a download URL for the processed CSV.

### Download Processed CSV

GET /download/{file_id}

Download the processed CSV file.

## Environment Variables

- GRPC_HOST: Host for gRPC server (default: localhost)
- GRPC_PORT: Port for gRPC server (default: 50051)
- FASTAPI_HOST: Host for FastAPI (default: 0.0.0.0)
- FASTAPI_PORT: Port for FastAPI (default: 8000)
- UPLOAD_DIR: Directory for uploads (default: uploads)

## Dependencies

- grpcio
- grpcio-tools
- fastapi
- python-multipart
- uvicorn
- black
- python-dotenv
