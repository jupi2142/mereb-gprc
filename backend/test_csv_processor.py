import csv
import io
import os
import tempfile
from collections import defaultdict

import pytest

from .celery_app import read_csv_rows, aggregate_sales, create_csv_from_aggregated


class TestReadCsvRows:
    def test_read_csv_rows_skips_header(self):
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', newline='', delete=False, suffix='.csv') as f:
            writer = csv.writer(f)
            writer.writerow(['Department Name', 'Date', 'Number of Sales'])
            writer.writerow(['Beauty', '2023-07-15', '924'])
            writer.writerow(['Sports', '2023-11-18', '942'])
            temp_file = f.name

        try:
            rows = list(read_csv_rows(temp_file))
            assert len(rows) == 2
            assert rows[0] == ['Beauty', '2023-07-15', '924']
            assert rows[1] == ['Sports', '2023-11-18', '942']
        finally:
            os.unlink(temp_file)

    def test_read_csv_rows_empty_file(self):
        with tempfile.NamedTemporaryFile(mode='w', newline='', delete=False, suffix='.csv') as f:
            writer = csv.writer(f)
            writer.writerow(['Department Name', 'Date', 'Number of Sales'])
            temp_file = f.name

        try:
            rows = list(read_csv_rows(temp_file))
            assert len(rows) == 0
        finally:
            os.unlink(temp_file)


class TestAggregateSales:
    def test_aggregate_sales_basic(self):
        rows = [
            ['Beauty', '2023-07-15', '100'],
            ['Sports', '2023-11-18', '200'],
            ['Beauty', '2023-09-30', '50'],
        ]
        sales = aggregate_sales((row for row in rows))
        expected = defaultdict(int, {'Beauty': 150, 'Sports': 200})
        assert dict(sales) == dict(expected)

    def test_aggregate_sales_with_invalid_rows(self):
        rows = [
            ['Beauty', '2023-07-15', '100'],
            ['Sports'],  # Invalid row
            ['Beauty', '2023-09-30', 'abc'],  # Invalid number
            ['Home', '2023-02-18', '50'],
        ]
        sales = aggregate_sales((row for row in rows))
        expected = defaultdict(int, {'Beauty': 100, 'Home': 50})
        assert dict(sales) == dict(expected)

    def test_aggregate_sales_with_progress_callback(self):
        rows = [
            ['Beauty', '2023-07-15', '100'],
            ['Sports', '2023-11-18', '200'],
            ['Beauty', '2023-09-30', '50'],
        ]
        progress_calls = []

        def progress_callback(*args):
            progress_calls.append(args)

        sales = aggregate_sales((row for row in rows), progress_callback=progress_callback, progress_interval=1)
        expected = defaultdict(int, {'Beauty': 150, 'Sports': 200})
        assert dict(sales) == dict(expected)
        assert len(progress_calls) == 4  # Called for each row + final

    @pytest.mark.parametrize("csv_file", ["test_csvs/test_sales1.csv", "test_csvs/test_sales2.csv", "test_csvs/test_sales3.csv"])
    def test_aggregate_sales_with_test_csvs(self, csv_file):
        if not os.path.exists(csv_file):
            pytest.skip(f"Test CSV {csv_file} not found")
        rows = read_csv_rows(csv_file)
        sales = aggregate_sales(rows)
        assert isinstance(sales, dict)
        assert len(sales) > 0
        # Check that all values are integers
        for dept, total in sales.items():
            assert isinstance(total, int)
            assert total >= 0


class TestCreateCsvFromAggregated:
    def test_create_csv_from_aggregated(self):
        sales = {'Beauty': 150, 'Sports': 200, 'Home': 50}
        output = io.StringIO()
        create_csv_from_aggregated(sales, output)
        output.seek(0)
        reader = csv.reader(io.StringIO(output.getvalue()))
        rows = list(reader)
        assert rows[0] == ['Department Name', 'Total Sales']
        # Sort the data rows for consistent comparison
        data_rows = sorted(rows[1:], key=lambda x: x[0])
        expected_data = [['Beauty', '150'], ['Home', '50'], ['Sports', '200']]
        assert data_rows == expected_data

    def test_create_csv_from_aggregated_empty(self):
        sales = {}
        output = io.StringIO()
        create_csv_from_aggregated(sales, output)
        output.seek(0)
        reader = csv.reader(io.StringIO(output.getvalue()))
        rows = list(reader)
        assert rows == [['Department Name', 'Total Sales']]