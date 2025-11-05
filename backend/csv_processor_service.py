import csv
import io
from collections import defaultdict
from csv_processor_pb2_grpc import CsvProcessorServicer
from csv_processor_pb2 import ProcessCsvResponse

class CsvProcessorService(CsvProcessorServicer):
    def ProcessCsv(self, request_iterator, context):
        # Accumulate all lines into a single CSV string
        csv_data = ""
        for request in request_iterator:
            csv_data += request.line

        # Parse the CSV data
        reader = csv.reader(io.StringIO(csv_data))
        sales = defaultdict(int)
        try:
            _ = next(reader)  # Skip header
            for row in reader:
                if len(row) < 3:
                    continue  # Skip invalid rows
                dept, _, num_sales = row
                sales[dept] += int(num_sales)
        except (ValueError, StopIteration):
            # Handle errors, perhaps return error response
            pass

        # Create the processed CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Department Name", "Total Sales"])
        for dept, total in sales.items():
            writer.writerow([dept, total])
        processed_csv = output.getvalue()

        return ProcessCsvResponse(processed_csv=processed_csv)