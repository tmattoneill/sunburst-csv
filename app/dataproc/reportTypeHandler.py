import unittest
import os
import csv
from hashlib import md5
from typing import List, Dict
import io


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
                "Named Threat",
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
                "Report Period Hit Count",
                "Tag Status",
                "Public Deck",
                "Comment Type",
                "Comment Text",
                "Threat Behavior",
                "Expected Behavior",
                "Malware Condition",
                "City",
                "Country",
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


class TestReportTypeHandler(unittest.TestCase):
    test_results = []

    @classmethod
    def tearDownClass(cls):
        print("Test Results:")
        print("------------------------------------------------")
        print("Submitted Value | Expected Value | Returned Value")
        print("------------------------------------------------")
        for result in cls.test_results:
            print(
                f"{result['submitted_value']:<15} | {str(result['expected_value']):<14} | {str(result['returned_value'])}")
        print("------------------------------------------------")

    def setUp(self):
        # Create temporary test CSV files
        self.no_match_csv = "no_match.csv"
        self.not_all_basic_csv = "not_all_basic.csv"
        self.extra_columns_csv = "extra_columns.csv"
        self.formatted_headers_csv = "formatted_headers.csv"
        self.basic_and_enhanced_csv = "basic_and_enhanced.csv"

        # Create CSV content
        self._create_csv(self.no_match_csv, [
            "Some", "Random", "Headers"
        ])
        self._create_csv(self.not_all_basic_csv, [
            "Incident", "Ad Tag ID", "Hash", "Tag Name"
        ])
        self._create_csv(self.extra_columns_csv, [
            "Incident", "Ad Tag ID", "Hash", "Tag Name", "Scan Type", "Hit Type", "Scan Date", "Scan ID", "Example",
            "csid", "Resolution Reason", "Extra1", "Extra2"
        ])
        self._create_csv(self.formatted_headers_csv, [
            "iNcIdEnT", "ad tAg ID", "hAsH", "tAg nAmE", "SCAN TYPE", "hit type", "scan date", "SCAN ID", "EXAMPLE",
            "CSID", "resolution reason"
        ])
        self._create_csv(self.basic_and_enhanced_csv, [
            "Incident", "Ad Tag ID", "Hash", "Tag Name", "Scan Type", "Hit Type", "Scan Date", "Scan ID", "Example",
            "csid", "Resolution Reason", "Mikey",
            "Comment Type", "Comment Text", "Threat Behavior", "Expected Behavior", "Malware Condition", "Named Threat"
        ])

    def tearDown(self):
        # Remove temporary test CSV files
        os.remove(self.no_match_csv)
        os.remove(self.not_all_basic_csv)
        os.remove(self.extra_columns_csv)
        os.remove(self.formatted_headers_csv)
        os.remove(self.basic_and_enhanced_csv)

    def _create_csv(self, filename, headers):
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["header1", "header2", "header3"])
            csv_writer.writerow(["header1", "header2", "header3"])
            csv_writer.writerow(["header1", "header2", "header3"])
            csv_writer.writerow(headers)

    def test_no_match(self):
        handler = ReportTypeHandler(self.no_match_csv)
        expected_value = []
        returned_value = handler.hash_headers()
        self.assertEqual(returned_value, expected_value)
        TestReportTypeHandler.test_results.append({
            "submitted_value": "no_match",
            "expected_value": expected_value,
            "returned_value": returned_value
        })

    def test_not_all_basic(self):
        handler = ReportTypeHandler(self.not_all_basic_csv)
        expected_value = []
        returned_value = handler.hash_headers()
        self.assertEqual(returned_value, expected_value)
        TestReportTypeHandler.test_results.append({
            "submitted_value": "not_all_basic",
            "expected_value": expected_value,
            "returned_value": returned_value
        })

    def test_extra_columns(self):
        handler = ReportTypeHandler(self.extra_columns_csv)
        expected_value = ['basic']
        returned_value = handler.hash_headers()
        self.assertEqual(returned_value, expected_value)
        TestReportTypeHandler.test_results.append({
            "submitted_value": "extra_columns",
            "expected_value": expected_value,
            "returned_value": returned_value
        })

    def test_formatted_headers(self):
        handler = ReportTypeHandler(self.formatted_headers_csv)
        expected_value = ['basic']
        returned_value = handler.hash_headers()
        self.assertEqual(returned_value, expected_value)
        TestReportTypeHandler.test_results.append({
            "submitted_value": "formatted_headers",
            "expected_value": expected_value,
            "returned_value": returned_value
        })

    def test_basic_and_enhanced(self):
        handler = ReportTypeHandler(self.basic_and_enhanced_csv)
        expected_value = ['basic', 'enhanced']
        returned_value = handler.hash_headers()
        self.assertEqual(returned_value, expected_value)
        TestReportTypeHandler.test_results.append({
            "submitted_value": "basic_and_enhanced",
            "expected_value": expected_value,
            "returned_value": returned_value
        })


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestReportTypeHandler))
    runner = unittest.TextTestRunner()
    runner.run(suite)