from csv_processor_pb2_grpc import CsvProcessorServicer
from csv_processor_pb2 import ProcessCsvResponse, GetProcessingResultResponse
from celery.result import AsyncResult
from celery_app import celery_app, process_csv_task


class CsvProcessorService(CsvProcessorServicer):
    def ProcessCsv(self, request, context):
        task = process_csv_task.delay(request.file_path)
        return ProcessCsvResponse(task_id=task.id, status=task.state)

    def GetProcessingResult(self, request, context):
        task_result = AsyncResult(request.task_id, app=celery_app)
        if task_result.state == "PENDING":
            return GetProcessingResultResponse(completed=False, status="PENDING")
        elif task_result.state == "SUCCESS":
            return GetProcessingResultResponse(
                processed_csv=task_result.result,
                completed=True,
                status="SUCCESS",
            )
        else:
            # Handle failure
            return GetProcessingResultResponse(completed=False)
