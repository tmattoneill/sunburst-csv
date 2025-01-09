import pandas as pd
import csv
import json
import sys
from typing import Dict, Optional, Tuple, List, TypedDict, Union
from pathlib import Path


class TreeNode(TypedDict):
    """Tree node with name, value and children."""
    name: str
    value: float
    children: List['TreeNode']


class TreeRoot(TypedDict):
    """Root node of tree."""
    name: str
    value: float
    children: List[TreeNode]


from datetime import datetime

class ReportMetadata(TypedDict):
    """Metadata for the report including report type, dates, and data tree."""
    report_type: str
    date_start: str
    date_end: str
    data: TreeRoot


class ReportProcessor:
    def __init__(self,
                 client_name: str = 'Client',
                 input_file: str = "sample_data.csv",
                 tree_order: List[str] = None,
                 data_path: str = "../data"):
        self.data_path = Path(data_path)
        self.raw_data_path = self.data_path / "raw" / input_file
        self.processed_data_path = self.data_path / "dataset.csv"
        self.sunburst_data_path = self.data_path / "sunburst_data.json"
        self.tree_order = tree_order or ['hit_type',
                                         'expected_behavior',
                                         'malware_condition',
                                         'provider_account',
                                         'incident']
        self.client_name = client_name
        self.tree: Union[TreeRoot, Dict] = {}
        self.report_type: str = ""
        self.date_start: str = ""
        self.date_end: str = ""

    def _extract_report_type(self) -> str:
        """Extract report type from the CSV file, skipping header rows."""
        try:
            with open(self.raw_data_path, 'r', encoding='utf-8') as f:
                # Skip initial blank rows if any
                report_type_line = ""
                for _ in range(4):  # Read first 4 lines to find report type
                    line = f.readline().strip()
                    if line and not line.startswith(','):  # Find first non-empty line that doesn't start with comma
                        report_type_line = line
                        break

                if report_type_line:
                    # Split and get first non-empty cell
                    cells = [cell.strip() for cell in report_type_line.split(',')]
                    report_type = next((cell for cell in cells if cell), "Unknown Report Type")
                    return report_type
                return "Unknown Report Type"
        except Exception as e:
            print(f"Error extracting report type: {str(e)}")
            return "Unknown Report Type"

    def process_raw_data(self) -> pd.DataFrame:
        """Process raw security data from CSV and create grouped dataset."""
        try:
            print(f"Attempting to read: {self.raw_data_path}")
            print(f"File exists: {self.raw_data_path.exists()}")

            # First read the metadata rows
            with open(self.raw_data_path, 'r', encoding='utf-8') as f:
                rows = []
                for _ in range(4):
                    rows.append(f.readline().strip())

                # Extract report type from first row, first cell
                self.report_type = rows[0].split(',')[0].strip('"')
                print(f"Extracted report type: {self.report_type}")

                # Extract and parse date span from second row
                date_span = rows[1].split(',')[0].strip('"')  # Get first cell of second row and remove quotes
                if ' - ' in date_span:
                    start_str, end_str = date_span.split(' - ')
                    # Clean up any remaining quotes and whitespace
                    start_str = start_str.strip().strip('"')
                    end_str = end_str.strip().strip('"')
                    # Parse dates and format them consistently
                    try:
                        start_date = datetime.strptime(start_str, '%m/%d/%Y %H:%M')
                        end_date = datetime.strptime(end_str, '%m/%d/%Y %H:%M')
                        self.date_start = start_date.strftime('%b. %-d, %Y')
                        self.date_end = end_date.strftime('%b. %-d, %Y')
                        print(f"Extracted date span: {self.date_start} to {self.date_end}")
                    except ValueError as e:
                        print(f"Error parsing dates: {e}")
                        self.date_start = start_str
                        self.date_end = end_str

            # Now read the actual data, skipping the first 3 rows (keep the header row)
            df = pd.read_csv(self.raw_data_path, skiprows=3)

            # Convert column names to lowercase and replace spaces with underscores
            df.columns = df.columns.str.lower().str.replace(' ', '_')
            print("\nActual columns after processing:", df.columns.tolist())

            # Group by the requested columns and count occurrences
            grouped_data = df.groupby(self.tree_order).size().reset_index(name='Count')

            # Sort by count in descending order
            grouped_data = grouped_data.sort_values('Count', ascending=False)

            # Save to CSV file
            grouped_data.to_csv(self.processed_data_path, index=False)
            print(f"\nProcessing complete. Data saved to '{self.processed_data_path}'")

            return grouped_data

        except FileNotFoundError:
            print(f"Error: Input file '{self.raw_data_path}' not found")
            raise
        except Exception as e:
            print(f"An error occurred during raw data processing: {str(e)}")
            raise

    @staticmethod
    def _process_row(row: list) -> Tuple[Optional[str], Optional[List[str]], Optional[float]]:
        """Process a single CSV row for the tree structure."""
        # Clean the row - remove empty strings and whitespace
        cleaned_row = [str(item).strip() for item in row if item and str(item).strip()]

        if not cleaned_row:
            return None, None, None

        path: List[str] = []
        value = None
        key = None

        for item in cleaned_row:
            if not item:  # Skip any remaining empty values
                continue

            # Try to convert to float (handle negative numbers and zero)
            try:
                test_val = float(item)
                # Don't count 0 as a number if it's the first item (could be a node name)
                if test_val == 0 and not path:
                    if key is None:
                        key = item
                    path.append(item)
                else:
                    value = test_val
                    break
            except ValueError:
                if key is None:
                    key = item
                path.append(item)

        return key, path, value

    def _update_json_tree(self, path: List[str], value: float) -> None:
        """Update the JSON tree with a new path and value."""
        # Initialize if this is the first entry
        if not self.tree:
            self.tree = TreeRoot(
                name=self.client_name,
                value=0,
                children=[]
            )

        # Update root value
        self.tree['value'] += value

        # Find or create top-level node
        top_name = path[0]
        top_node = None
        for child in self.tree['children']:
            if child['name'] == top_name:
                top_node = child
                break

        if top_node is None:
            top_node = TreeNode(
                name=top_name,
                value=value,
                children=[]
            )
            self.tree['children'].append(top_node)
        else:
            top_node['value'] += value

        # Process remaining path elements
        current: TreeNode = top_node
        for i, name in enumerate(path[1:], 1):
            # Look for existing node
            next_node = None
            for child in current['children']:
                if child['name'] == name:
                    next_node = child
                    break

            if next_node is None:
                next_node = TreeNode(
                    name=name,
                    value=value,
                    children=[]
                )
                current['children'].append(next_node)
            else:
                next_node['value'] += value

            current = next_node

    def create_sunburst_data(self) -> ReportMetadata:
        """Create hierarchical data structure from processed CSV."""
        try:
            # Reset the tree
            self.tree = {}

            # Process the CSV one row at a time
            with open(self.processed_data_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header

                for row in reader:
                    try:
                        key, path, value = self._process_row(row)
                        if key and path and value is not None:
                            self._update_json_tree(path, value)
                    except Exception as e:
                        print(f"Warning: Error processing row {row}: {str(e)}")
                        continue

            # Create the metadata object
            metadata = ReportMetadata(
                report_type=self.report_type,
                date_start=self.date_start,
                date_end=self.date_end,
                data=self.tree
            )

            # Save the result
            with open(self.sunburst_data_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(f"Data created and saved to {self.sunburst_data_path}")
            return metadata

        except Exception as e:
            print(f"Error creating data structure: {str(e)}")
            raise

    def process_all(self) -> ReportMetadata:
        """Run the complete processing pipeline."""
        self.process_raw_data()
        return self.create_sunburst_data()


if __name__ == "__main__":
    processor = ReportProcessor("Criteo", "criteo 30 day - malware- Security Incidents by Tag (1).csv")
    processor.process_all()
