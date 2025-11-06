import csv
import io
import os
import uuid
from collections import defaultdict

import csv_processor_pb2
import csv_processor_pb2_grpc
import grpc
import uvicorn
from celery_app import celery_app
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile, request: Request):
    # Save uploaded file
    upload_id = str(uuid.uuid4())
    upload_path = os.path.join(UPLOAD_DIR, f"{upload_id}.csv")
    with open(upload_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # Read and write in 1MB chunks
            f.write(chunk)

    # Call gRPC service with file path
    grpc_host = os.getenv("GRPC_HOST", "localhost")
    grpc_port = os.getenv("GRPC_PORT", "50051")
    with grpc.insecure_channel(f"{grpc_host}:{grpc_port}") as channel:
        stub = csv_processor_pb2_grpc.CsvProcessorStub(channel)
        response = stub.ProcessCsv(
            csv_processor_pb2.ProcessCsvRequest(file_path=upload_path)
        )
        task_id = response.task_id
        status = response.status

    download_url = request.url_for("download_file", file_id=task_id)
    return {
        "download_url": str(download_url),
        "status": status,
        "task_id": task_id,
    }


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    grpc_host = os.getenv("GRPC_HOST", "localhost")
    grpc_port = os.getenv("GRPC_PORT", "50051")

    with grpc.insecure_channel(f"{grpc_host}:{grpc_port}") as channel:
        stub = csv_processor_pb2_grpc.CsvProcessorStub(channel)
        response = stub.GetProcessingResult(
            csv_processor_pb2.GetProcessingResultRequest(task_id=task_id)
        )
        return {
            "completed": response.completed,
            "processed_csv": response.processed_csv,
            "status": response.status,
            "progress": {
                "lines_processed": response.progress.lines_processed,
                "departments": response.progress.departments,
                "time_elapsed": response.progress.time_elapsed,
            },
        }


@app.api_route("/download/{file_id}", methods=["GET", "HEAD"])
async def download_file(file_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_result.csv")
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="text/csv",
            filename=f"{file_id}_result.csv",
        )
    else:
        return JSONResponse(content={"error": "File not found"}, status_code=404)


if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
