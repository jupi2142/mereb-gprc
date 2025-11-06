from collections import defaultdict
import csv
import io
from time import sleep
import typing
from celery import Celery
import os
from typing import Generator, Dict, List

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

celery_app = Celery(
    "csv_processor",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


def read_csv_rows(file_path: str) -> Generator[List[str], None, None]:
    with open(file_path, "r", newline="") as f:
        reader = csv.reader(f)
        try:
            _ = next(reader)  # Skip header
            for row in reader:
                yield row
        except StopIteration:
            pass


def aggregate_sales(rows: Generator[List[str], None, None]) -> Dict[str, int]:
    sales = defaultdict(int)
    for row in rows:
        if len(row) < 3:
            continue  # Skip invalid rows
        dept, _, num_sales = row
        try:
            sales[dept] += int(num_sales)
        except ValueError:
            pass  # Handle errors
    return sales


def create_csv_from_aggregated(sales: Dict[str, int], output: typing.TextIO) -> None:
    writer = csv.writer(output)
    writer.writerow(["Department Name", "Total Sales"])
    for dept, total in sales.items():
        writer.writerow([dept, total])
    output.seek(0)  # Reset to beginning for reading


@celery_app.task
def process_csv_task(file_path: str) -> str:
    sleep(5)
    rows = read_csv_rows(file_path)
    sales = aggregate_sales(rows)
    result_path = os.path.join(UPLOAD_DIR, f"{process_csv_task.request.id}_result.csv")
    with open(result_path, "w", newline="") as f:
        create_csv_from_aggregated(sales, f)

    return result_path


# Auto-discover tasks from all modules
celery_app.autodiscover_tasks()
