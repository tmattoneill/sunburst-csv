import os
import csv
from hashlib import md5
from typing import List, Dict


class ReportTypeHandler:
    def __init__(self, csv_file_path: str):
        self.reportTypes: Dict[str, List[str]] = {
            'basic': [
                "Incident",
                "Ad Tag ID",
                "Hash",
                "Tag Name",
                "Scan Type",
                "Hit Type",
                "Scan Date",
                "Scan ID",
                "Example",
                "csid",
                "Resolution Reason"
            ],
            'enhanced': [
                "Incident",
                "Ad Tag ID",
                "Hash",
                "Tag Name",
                "Scan Type",
                "Hit Type",
                "Scan Date",
                "Scan ID",
                "Example",
                "csid",
                "Comment Type",
                "Comment Text",
                "Threat Behavior",
                "Expected Behavior",
                "Malware Condition",
                "Resolution Reason"
            ],
            'detailed': [
                "Incident",
                "Ad Tag ID",
                "Hash",
                "Tag Name",
                "Scan Type",
                "Hit Type",
                "Scan Date",
                "Scan ID",
                "Example",
                "csid",
                "Start Date",
                "End Date",
                "Pause",
                "Priority",
                "Publisher Name",
                "Publisher ID",
                "Website ID",
                "Website Name",
                "Provider ID",
                "Provider Name",
                "Provider Account ID",
                "Provider Account",
                "Country",
                "Referrer",
                "Comment Type",
                "Comment Text",
                "Threat Behavior",
                "Expected Behavior",
                "Malware Condition",
                "City",
                "Named Threat",
                "Resolution Reason"
            ],
            'full': [
                "Incident",
                "Ad Tag ID",
                "Hash",
                "Tag Name",
                "Scan Type",
                "Hit Type",
                "Scan Date",
                "Scan ID",
                "Example",
                "csid",
                "Report Period Hit Count",
                "Tag Status",
                "Start Date",
                "End Date",
                "Pause",
                "Priority",
                "Publisher Name",
                "Publisher ID",
                "Website ID",
                "Website Name",
                "Provider ID",
                "Provider Name",
                "Provider Account ID",
                "Provider Account",
                "Country",
                "Referrer",
                "Public Deck",
                "Comment Type",
                "Comment Text",
                "Threat Behavior",
                "Expected Behavior",
                "Malware Condition",
                "Extracted Source",
                "City",
                "Named Threat",
                "Resolution Reason"
            ]
        }
        self.headers: List[str] = self._read_headers_from_csv(csv_file_path)
        self.internal_hashes = dict(self._internal_hashes())

    @staticmethod
    def _read_headers_from_csv(self, csv_file_path: str) -> List[str]:
        headers = []
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for i, row in enumerate(csv_reader):
                if i == 3:  # Headers are on the 4th row (index 3)
                    headers = [header.lower() for header in row]
                    break
        return headers

    def hash_headers(self):

        matching_report_types = []
        for report_type, required_headers in self.reportTypes.items():
            if all(header.lower() in self.headers for header in required_headers):
                matching_report_types.append(report_type)

        return matching_report_types

    def _internal_hashes(self):
        for reportType, headers in self.reportTypes.items():
            concat_headers = ''.join(headers)
            yield reportType, md5(concat_headers.encode()).hexdigest()

    @staticmethod
    def get_chart_fields(self, report_type: str):
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
                         'tag name']
        }

        return chart_field_ordering[report_type]


if __name__ == '__main__':
    directory_path = "../../data/raw"  # Specify the directory path here

    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            try:
                handler = ReportTypeHandler(file_path)
                report_types = handler.hash_headers()
                print(f"File: {filename}, Report Types: {report_types}")
            except Exception as e:
                 print(f"Error processing {filename}: {e}")