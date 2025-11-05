from collections import defaultdict
import csv
import io
from celery import Celery
import os

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


@celery_app.task
def process_csv_task(lines):
    # Parse the CSV data from the lines list
    reader = csv.reader(lines)
    sales = defaultdict(int)
    try:
        _ = next(reader)  # Skip header
        for row in reader:
            if len(row) < 3:
                continue  # Skip invalid rows
            dept, _, num_sales = row
            sales[dept] += int(num_sales)
    except (ValueError, StopIteration):
        # Handle errors
        pass

    # Create the processed CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Department Name", "Total Sales"])
    for dept, total in sales.items():
        writer.writerow([dept, total])
    processed_csv = output.getvalue()

    return processed_csv


# Auto-discover tasks from all modules
celery_app.autodiscover_tasks()
