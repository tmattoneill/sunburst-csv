import sqlite3
from contextlib import contextmanager
from typing import Dict, FrozenSet, List, Set
import logging
from pathlib import Path


class SecurityDataHandler:
    def __init__(self, db_path: str = "../../data/security.db"):
        self.db_path = db_path
        # Keep the same report type definitions but with normalized field names
        self.report_types = self._initialize_report_types()

        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def normalize_field_name(field_name: str) -> str:
        """
        Normalizes field names to a consistent format by:
        - converting to lowercase
        - stripping whitespace
        - replacing spaces with underscores
        """
        return field_name.lower().strip().replace(' ', '_')

    def _initialize_report_types(self) -> Dict[str, FrozenSet[str]]:
        """Initialize report types with normalized field names"""
        basic_fields = [
            "incident", "ad tag id", "hash", "tag name", "scan type",
            "hit type", "scan date", "scan id", "example", "csid",
            "resolution reason"
        ]

        enhanced_fields = basic_fields + [
            "comment type", "comment text", "threat behavior",
            "expected behavior", "malware condition"
        ]

        detailed_fields = enhanced_fields + [
            "start date", "end date", "pause", "priority",
            "publisher name", "publisher id", "website id",
            "website name", "provider id", "provider name",
            "provider account id", "provider account", "country",
            "referrer", "city", "named threat"
        ]

        full_fields = detailed_fields + [
            "report period hit count", "tag status", "public deck",
            "extracted source"
        ]

        raw_types = {
            'basic': basic_fields,
            'enhanced': enhanced_fields,
            'detailed': detailed_fields,
            'full': full_fields
        }

        return {
            type_name: frozenset(self.normalize_field_name(field) for field in fields)
            for type_name, fields in raw_types.items()
        }

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def get_available_columns(self) -> Set[str]:
        """Get all available columns from the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(security_data)")
            return {row[1] for row in cursor.fetchall()}

    def get_present_fields(self, fields_to_check: Set[str]) -> Set[str]:
        """
        Check which fields have actual values in the database.
        Returns normalized field names that have data.
        """
        normalized_fields = {self.normalize_field_name(f) for f in fields_to_check}
        fields_with_values = set()

        self.logger.info(f"Checking fields: {normalized_fields}")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get all column names from the table
            db_columns = self.get_available_columns()
            self.logger.info(f"Available columns in DB: {db_columns}")

            for field in normalized_fields:
                if field not in db_columns:
                    self.logger.info(f"Field not in database: {field}")
                    continue

                # Check if field has any non-null, non-empty values
                cursor.execute(f"""
                    SELECT COUNT(*) FROM security_data 
                    WHERE {field} IS NOT NULL 
                    AND trim({field}) != ''
                    LIMIT 1
                """)
                if cursor.fetchone()[0] > 0:
                    fields_with_values.add(field)
                    self.logger.info(f"Found data for field: {field}")
                else:
                    self.logger.info(f"No data found for field: {field}")

        return fields_with_values

    def detect_report_type(self) -> List[str]:
        """
        Detect which report type(s) match the available columns.
        Similar to the original hash_headers but using DB columns.
        """
        available_columns = self.get_available_columns()
        self.logger.info(f"Detecting report type from columns: {available_columns}")

        matching_types = []
        for report_type, required_fields in self.report_types.items():
            if required_fields.issubset(available_columns):
                matching_types.append(report_type)

        self.logger.info(f"Matching report types: {matching_types}")
        return matching_types

    def get_chart_fields(self, report_type: str) -> List[str]:
        """
        Returns the appropriate chart fields based on the report type.
        Only returns fields that actually have data in the database.
        """
        base_fields = {
            'basic': ["scan_type", "hit_type", "incident", "tag_name"],
            'enhanced': ["hit_type", "threat_behavior", "malware_condition",
                         "incident", "tag_name"],
            'detailed': ["publisher_name", "website_name", "provider_name",
                         "country", "hit_type", "named_threat", "threat_behavior",
                         "malware_condition", "incident", "tag_name"],
            'full': ["publisher_name", "website_name", "provider_name",
                     "country", "hit_type", "named_threat", "threat_behavior",
                     "malware_condition", "incident", "tag_name"]
        }

        if report_type not in base_fields:
            self.logger.warning(f"Unknown report type: {report_type}")
            return []

        if report_type in ('detailed', 'full'):
            # Check which detail fields actually have data
            detail_fields = {
                "publisher_name", "website_name",
                "provider_name", "provider_account", "country"
            }
            available_details = self.get_present_fields(detail_fields)

            if available_details:
                # Return available detail fields plus standard fields
                standard_fields = ["hit_type", "named_threat", "threat_behavior",
                                   "malware_condition", "incident", "tag_name"]
                return list(available_details) + standard_fields

        # For basic and enhanced, or if no detail fields have data
        return base_fields[report_type]


if __name__ == "__main__":
    # Example usage
    handler = SecurityDataHandler()

    # Detect report type
    report_types = handler.detect_report_type()
    print(f"Detected report types: {report_types}")

    # Get chart fields for each type
    for report_type in report_types:
        fields = handler.get_chart_fields(report_type)
        print(f"\nChart fields for {report_type}:")
        print(fields)