from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import FileResponse
import uuid
import os
import csv
from collections import defaultdict
import io
import uvicorn
import grpc
from dotenv import load_dotenv
import grpc_server.csv_processor_pb2_grpc
import grpc_server.csv_processor_pb2

load_dotenv()

app = FastAPI()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload")
async def upload_file(file: UploadFile, request: Request):
    file.file.seek(0)

    # Call gRPC service with streaming
    def request_generator():
        for line in file.file:
            yield grpc_server.csv_processor_pb2.ProcessCsvRequest(
                line=line.decode("utf-8")
            )

    grpc_host = os.getenv("GRPC_HOST", "localhost")
    grpc_port = os.getenv("GRPC_PORT", "50051")
    with grpc.insecure_channel(f"{grpc_host}:{grpc_port}") as channel:
        stub = grpc_server.csv_processor_pb2_grpc.CsvProcessorStub(channel)
        response = stub.ProcessCsv(request_generator())

    result_id = str(uuid.uuid4())
    result_path = os.path.join(UPLOAD_DIR, f"{result_id}.csv")
    with open(result_path, "w", newline="") as f:
        f.write(response.processed_csv)

    download_url = request.url_for("download_file", file_id=result_id)
    return {"download_url": str(download_url)}


@app.get("/download/{file_id}")
async def download_file(file_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="text/csv",
            filename=f"{file_id}.csv",
        )
    else:
        return {"error": "File not found"}


if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
