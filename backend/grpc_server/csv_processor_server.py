import grpc
from concurrent import futures
import os
from dotenv import load_dotenv
import csv_processor_pb2_grpc
from csv_processor_service import CsvProcessorService

load_dotenv()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    csv_processor_pb2_grpc.add_CsvProcessorServicer_to_server(
        CsvProcessorService(), server
    )
    grpc_port = os.getenv("GRPC_PORT", "50051")
    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    print(f"gRPC server started on port {grpc_port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
