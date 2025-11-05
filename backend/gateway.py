from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import FileResponse
import uuid
import os
import csv
from collections import defaultdict
import io
import uvicorn

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def aggregate_sales(reader):
    sales = defaultdict(int)
    _ = next(reader)  # Skip header
    for row in reader:
        dept, _, num_sales = row
        sales[dept] += int(num_sales)
    return sales


@app.post("/upload")
async def upload_file(file: UploadFile, request: Request):
    file.file.seek(0)
    reader = csv.reader(io.TextIOWrapper(file.file, encoding="utf-8"))
    sales = aggregate_sales(reader)

    result_id = str(uuid.uuid4())
    result_path = os.path.join(UPLOAD_DIR, f"{result_id}.csv")
    with open(result_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Department Name", "Total Sales"])
        for dept, total in sales.items():
            writer.writerow([dept, total])

    download_url = request.url_for('download_file', file_id=result_id)
    return {"download_url": str(download_url)}


@app.get("/download/{file_id}")
async def download_file(file_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv", filename=f"{file_id}.csv",)
    else:
        return {"error": "File not found"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)