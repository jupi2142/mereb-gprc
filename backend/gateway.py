import os
from contextlib import asynccontextmanager

import csv_processor_pb2
import csv_processor_pb2_grpc
import grpc
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

load_dotenv()

# Global gRPC channel and stub for performance
grpc_host = os.getenv("GRPC_HOST", "localhost")
grpc_port = os.getenv("GRPC_PORT", "50051")
grpc_channel = None
grpc_stub = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global grpc_channel, grpc_stub
    grpc_channel = grpc.aio.insecure_channel(f"{grpc_host}:{grpc_port}")
    grpc_stub = csv_processor_pb2_grpc.CsvProcessorStub(grpc_channel)
    yield
    await grpc_channel.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_file(file: UploadFile, request: Request):
    # Stream file content in chunks
    async def chunk_generator():
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            yield csv_processor_pb2.CsvChunk(data=chunk)

    response = await grpc_stub.ProcessCsv(chunk_generator())
    task_id = response.task_id
    status = response.status

    return {
        "status": status,
        "task_id": task_id,
        "download_url": str(request.url_for("download_file", task_id=task_id)),
    }


@app.get("/status/{task_id}")
async def get_status(task_id: str):
    response = await grpc_stub.GetProcessingResult(
        csv_processor_pb2.GetProcessingResultRequest(task_id=task_id)
    )
    return {
        "completed": response.completed,
        "status": response.status,
        "progress": {
            "lines_processed": response.progress.lines_processed,
            "departments": response.progress.departments,
            "time_elapsed": response.progress.time_elapsed,
        },
    }


@app.get("/download/{task_id}")
async def download_file(task_id: str):
    # Check completion using global stub
    status_response = await grpc_stub.GetProcessingResult(
        csv_processor_pb2.GetProcessingResultRequest(task_id=task_id)
    )

    if not status_response.completed:
        return JSONResponse(
            content={"error": "Processing not completed"}, status_code=400
        )

    # Stream using global stub
    async def stream_generator():
        async for chunk in grpc_stub.DownloadResult(
            csv_processor_pb2.DownloadResultRequest(task_id=task_id)
        ):
            yield chunk.data

    return StreamingResponse(
        stream_generator(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={task_id}_result.csv"},
    )


if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
