import ipdb
from csv_processor_pb2_grpc import CsvProcessorServicer
from csv_processor_pb2 import ProcessCsvResponse, GetProcessingResultResponse, Progress
from celery.result import AsyncResult
from celery_app import celery_app, process_csv_task


class CsvProcessorService(CsvProcessorServicer):
    def ProcessCsv(self, request, context):
        task = process_csv_task.delay(request.file_path)
        return ProcessCsvResponse(task_id=task.id, status=task.state)

    def GetProcessingResult(self, request, context):
        task_result = AsyncResult(request.task_id, app=celery_app)
        if task_result.state == "PENDING":
            progress = (
                Progress(
                    lines_processed=task_result.info.get("lines_processed", 0),
                    departments=task_result.info.get("departments", 0),
                    time_elapsed=task_result.info.get("time_elapsed", 0.0),
                )
                if task_result.info
                else Progress(lines_processed=0, departments=0, time_elapsed=0.0)
            )
            return GetProcessingResultResponse(
                completed=False,
                status="PENDING",
                progress=progress,
            )
        elif task_result.state == "SUCCESS":
            progress = (
                Progress(
                    lines_processed=task_result.info.get("lines_processed", 0),
                    departments=task_result.info.get("departments", 0),
                    time_elapsed=task_result.info.get("time_elapsed", 0.0),
                )
                if task_result.info
                else Progress(lines_processed=0, departments=0, time_elapsed=0.0)
            )
            return GetProcessingResultResponse(
                processed_csv=task_result.info.get('result_path'),
                completed=True,
                status="SUCCESS",
                progress=progress,
            )
        else:
            # Handle failure
            return GetProcessingResultResponse(
                completed=False,
                status="FAILURE",
                progress=Progress(lines_processed=0, departments=0, time_elapsed=0.0),
            )
