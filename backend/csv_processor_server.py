import grpc
from concurrent import futures
import csv_processor_pb2_grpc
from csv_processor_service import CsvProcessorService

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    csv_processor_pb2_grpc.add_CsvProcessorServicer_to_server(CsvProcessorService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()