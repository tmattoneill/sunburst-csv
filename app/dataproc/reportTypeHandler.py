import csv
import hashlib
import logging
import re
from pathlib import Path
from typing import Dict, FrozenSet, List, Set
from itertools import islice

class ReportTypeHandler:
    def __init__(self, csv_file_path: str):
        self.report_types: Dict[str, FrozenSet[str]] = {
            'basic': frozenset([
                "incident",
                "ad tag id",
                "hash",
                "tag name",
                "scan type",
                "hit type",
                "scan date",
                "scan id",
                "example",
                "csid",
                "resolution reason"
            ]),
            'enhanced': frozenset([
                "incident",
                "ad tag id",
                "hash",
                "tag name",
                "scan type",
                "hit type",
                "scan date",
                "scan id",
                "example",
                "csid",
                "comment type",
                "comment text",
                "threat behavior",
                "expected behavior",
                "malware condition",
                "resolution reason"
            ]),
            'detailed': frozenset([
                "incident",
                "ad tag id",
                "hash",
                "tag name",
                "scan type",
                "hit type",
                "scan date",
                "scan id",
                "example",
                "csid",
                 "start date",
                "end date",
                "pause",
                "priority",
                "publisher name",
                "publisher id",
                "website id",
                "website name",
                "provider id",
                "provider name",
                "provider account id",
                "provider account",
                "country",
                "referrer",
                "comment type",
                "comment text",
                "threat behavior",
                "expected behavior",
                "malware condition",
                 "city",
                "named threat",
                "resolution reason"
            ]),
            'full': frozenset([
                "incident",
                "ad tag id",
                "hash",
                "tag name",
                "scan type",
                "hit type",
                "scan date",
                "scan id",
                "example",
                "csid",
                "report period hit count",
                "tag status",
                 "start date",
                "end date",
                "pause",
                "priority",
                "publisher name",
                "publisher id",
                "website id",
                "website name",
                "provider id",
                "provider name",
                "provider account id",
                "provider account",
                "country",
                "referrer",
                 "public deck",
                "comment type",
                "comment text",
                "threat behavior",
                "expected behavior",
                "malware condition",
                 "extracted source",
                "city",
                 "named threat",
                "resolution reason"
            ])
        }
        self.headers: FrozenSet[str] = self._read_headers_from_csv(csv_file_path)
        self.internal_hashes = dict(self._internal_hashes())


    def _read_headers_from_csv(self, csv_file_path: str) -> FrozenSet[str]:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for i, row in enumerate(csv_reader):
                if i == 3:
                     # Normalize headers: lowercase and remove extra spaces
                    headers = [re.sub(r'\s+', ' ', header).lower().strip() for header in row]
                    return frozenset(headers)


    def hash_headers(self) -> List[str]:
        return [
            report_type
            for report_type, required_headers
            in self.report_types.items()
            if required_headers.issubset(self.headers)
        ]


    def _internal_hashes(self) -> Dict[str, str]:
        for report_type, headers in self.report_types.items():
            concat_headers = "".join(headers)
            yield report_type, hashlib.md5(concat_headers.encode()).hexdigest()

    @staticmethod
    def normalize_field_name(field_name: str) -> str:
        """
        Normalizes field names to a consistent format by:
        - converting to lowercase
        - stripping whitespace
        - replacing spaces with underscores

        Args:
            field_name: The field name to normalize

        Returns:
            str: Normalized field name
        """
        return field_name.lower().strip().replace(' ', '_')

    @staticmethod
    def _get_present_fields(csv_file_path: str) -> Set[str]:
        """
        Helper function to check which fields have actual values in the CSV data.
        Only checks the first 10 rows for efficiency.
        """
        # Ensure logging is configured
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

        logging.info(f"Starting _get_present_fields with file: {csv_file_path}")  # Add this line

        fields_with_values = set()
        fields_to_check = {
            "website name",
            "publisher name",
            "provider name",
            "provider account",
            "country",
        }

        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            logging.info("File opened successfully")  # Add this line

            # Skip the first 3 rows to get to actual headers
            for i in range(3):  # Changed to track iteration
                line = next(csvfile)
                logging.info(f"Skipped line {i + 1}: {line.strip()}")  # Add this line

            # Read headers and normalize them
            headers = next(csvfile).strip().split(',')
            logging.info(f"Original headers: {headers}")

            normalized_headers = [re.sub(r'\s+', ' ', h.lower().strip()) for h in headers]
            logging.info(f"Normalized headers: {normalized_headers}")

            header_mapping = dict(zip(normalized_headers, headers))
            logging.info(f"Header mapping: {header_mapping}")

            # Reset file pointer and skip headers again
            csvfile.seek(0)
            for _ in range(4):
                next(csvfile)

            csv_reader = csv.DictReader(csvfile, fieldnames=headers)

            for row in islice(csv_reader, 10):  # Check first 10 rows
                for field in fields_to_check:
                    # Debug logging for field matching
                    orig_field = header_mapping.get(field)
                    if orig_field:
                        value = row.get(orig_field, '').strip()
                        logging.info(f"Checking field '{field}' (original: '{orig_field}'): Value = '{value}'")
                        if value:
                            fields_with_values.add(field)
                            logging.info(f"Data found in {field}: {value}")
                    else:
                        logging.info(f"No mapping found for field: {field}")

            logging.info(f"Fields with values: {fields_with_values}")
            return fields_with_values


    @staticmethod
    def get_chart_fields(report_type: str, csv_file_path:str = None) -> List[str]:
            """
            Returns the appropriate chart fields based on the report type
            """
            if report_type in ("detailed", "full"):
                if not csv_file_path:
                    raise ValueError(f"csv_file_path required when report_type is detailed or full")

                present_fields = ReportTypeHandler._get_present_fields(csv_file_path)
                chart_fields = []

                if "publisher name" in present_fields:
                    chart_fields.append("publisher name")
                if "website name" in present_fields:
                     chart_fields.append("website name")
                if "provider name" in present_fields:
                     chart_fields.append("provider name")
                if "country" in present_fields:
                     chart_fields.append("country")

                if chart_fields:
                    return chart_fields + [
                                "hit type",
                                "named threat",
                                "threat behavior",
                                "malware condition",
                                "incident",
                                "tag name"
                            ]


            chart_field_ordering = {
                'basic': ["scan type",
                            "hit type",
                            "incident",
                            "tag name"],
                'enhanced': ['hit type',
                             'threat behavior',
                             'malware condition',
                             'incident',
                             'tag name'],
               'detailed': ['publisher name',
                             'website name',
                             'provider name',
                             'country',
                             'hit type',
                             'named threat',
                             'threat behavior',
                             'malware condition',
                             'incident',
                             'tag name'],
                'full': ['publisher name',
                             'website name',
                             'provider name',
                             'country',
                             'hit type',
                             'named threat',
                             'threat behavior',
                             'malware condition',
                             'incident',
                             'tag name']
            }

            return chart_field_ordering.get(report_type, [])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    directory_path = Path(__file__).parent / "../../data/raw"
    logging.info(f"Processing CSV files in: {directory_path}")

    for file_path in directory_path.glob("*.csv"):
        try:
            handler = ReportTypeHandler(str(file_path))
            report_types = handler.hash_headers()
            for report_type in report_types:
              chart_fields = ReportTypeHandler.get_chart_fields(report_type, str(file_path))
              logging.info(f"File: {file_path.name}, Report Type: {report_type}, Chart Fields: {chart_fields}")
        except Exception as e:
             logging.error(f"Error processing {file_path.name}: {e}")