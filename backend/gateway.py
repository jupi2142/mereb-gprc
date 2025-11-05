from fastapi import FastAPI, UploadFile, FileResponse
import uuid
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"file_id": file_id}

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='text/csv', filename=f"{file_id}.csv")
    else:
        return {"error": "File not found"}