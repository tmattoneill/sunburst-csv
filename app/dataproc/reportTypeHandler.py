from hashlib import md5
from typing import List, Dict

class ReportTypeHandler:
    def __init__(self, headers: List[str]):
        self.reportTypes: Dict[str,List[str]] = {
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
            'detailed':  [
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
        self.headers: List[str] = [header.lower() for header in headers]
        self.internal_hashes = dict(self._internal_hashes())

    def hash_headers(self):
        concat_headers = ''.join(self.headers)
        return md5(concat_headers.encode()).hexdigest()

    def _internal_hashes(self):
        for reportType, headers in self.reportTypes.items():
            concat_headers = ''.join(headers)
            print(reportType, md5(concat_headers.encode()).hexdigest())
            yield reportType, md5(concat_headers.encode()).hexdigest()


if __name__ == "__main__":
    handler = ReportTypeHandler(['Report Type', 'Start Date', 'End Date'])
    print(handler.hash_headers())

