import csv
import os
import time
import typing
from collections import defaultdict
from typing import Callable, Dict, Generator, List

from celery import Celery

RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
if not os.path.isabs(RESULTS_DIR):
    RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), RESULTS_DIR))
os.makedirs(RESULTS_DIR, exist_ok=True)

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


def aggregate_sales(
    rows: Generator[List[str], None, None],
    progress_callback: Callable[[int, int], None] = None,
    progress_interval: int = 10,
) -> Dict[str, int]:
    sales = defaultdict(int)
    for row_number, row in enumerate(rows, start=1):
        if len(row) < 3:
            continue  # Skip invalid rows
        dept, _, num_sales = row
        try:
            sales[dept] += int(num_sales)
        except ValueError:
            pass  # Handle errors
        if progress_callback and row_number % progress_interval == 0:
            progress_callback(row_number, len(sales))
            time.sleep(0.3)
    if progress_callback:
        progress_callback(row_number, len(sales), "SUCCESS")
    return sales


def create_csv_from_aggregated(sales: Dict[str, int], output: typing.TextIO) -> None:
    writer = csv.writer(output)
    writer.writerow(["Department Name", "Total Sales"])
    for dept, total in sales.items():
        writer.writerow([dept, total])
    output.seek(0)  # Reset to beginning for reading


@celery_app.task(bind=True)
def process_csv_task(self, file_path: str) -> dict:
    rows = read_csv_rows(file_path)
    start_time = time.time()
    result_path = os.path.join(RESULTS_DIR, f"{process_csv_task.request.id}_result.csv")
    progress_dict = {
        "lines_processed": 0,
        "departments": 0,
        "time_elapsed": 0.0,
        "result_path": result_path,
    }

    def report_progress(current: int, departments: int, state: str = "PENDING"):
        time_elapsed = time.time() - start_time
        progress_dict.update(
            {
                "lines_processed": current,
                "departments": departments,
                "time_elapsed": time_elapsed,
            }
        )
        self.update_state(
            state=state,
            meta=progress_dict,
        )

    sales = aggregate_sales(rows, progress_callback=report_progress)
    with open(result_path, "w", newline="") as f:
        create_csv_from_aggregated(sales, f)

    return progress_dict


# Auto-discover tasks from all modules
celery_app.autodiscover_tasks()
