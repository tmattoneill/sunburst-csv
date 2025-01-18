import pandas as pd
import csv
import json
from typing import Dict, Optional, Tuple, List, TypedDict, Union
from pathlib import Path
import os
from .db_handler import DatabaseHandler
from .security_data_handler import SecurityDataHandler

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
    tree_order: List[str]


class ReportProcessor:
    def __init__(self,
                 client_name: str = 'Client',
                 input_file: str = "sample_data.csv",
                 tree_order: List[str] = None,
                 data_path: str = "../data"):
        self.data_path = Path(os.getenv('DATA_PATH', "../data"))
        self.raw_data_path = self.data_path / "raw" / input_file
        self.processed_data_path = self.data_path / "dataset.csv"
        self.sunburst_data_path = self.data_path / "sunburst_data.json"
        self.client_name = client_name
        self.tree: Union[TreeRoot, Dict] = {}
        self.report_type: str = ""
        self.date_start: str = ""
        self.date_end: str = ""
        self.required_columns = {
            'basic': ['incident', 'tag_name', 'hit_type'],
            'enhanced': ['incident', 'tag_name', 'hit_type', 'threat_behavior'],
            'detailed': ['incident', 'tag_name', 'hit_type', 'publisher_name', 'country'],
            'full': ['incident', 'tag_name', 'hit_type', 'publisher_name', 'country', 'report_period_hit_count', 'tag_status']
        }

        # Initialize handlers
        self.db_handler = DatabaseHandler(str(self.data_path / "security.db"))  # Use persistent DB
        self.security_handler = SecurityDataHandler(str(self.data_path / "security.db"))  # Pass same path

        # We'll set tree_order after processing the data
        self.tree_order: List[str] = tree_order or []

    def validate_file_structure(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate the dataframe structure and content.
        Returns (is_valid, error_message).
        """
        if df is None or df.empty:
            return False, "File is empty or could not be read"

        # Check for minimum row count (excluding headers)
        if len(df) < 1:
            return False, "File contains no data rows"

        # Normalize column names for comparison
        df_columns = set(col.lower().strip().replace(' ', '_') for col in df.columns)

        # Try to match against our known report types
        valid_structure = False
        missing_columns = []

        for report_type, required_cols in self.required_columns.items():
            normalized_required = set(col.lower().strip().replace(' ', '_')
                                      for col in required_cols)
            if normalized_required.issubset(df_columns):
                valid_structure = True
                break
            else:
                missing = normalized_required - df_columns
                if len(missing) < len(missing_columns) or not missing_columns:
                    missing_columns = missing

        if not valid_structure:
            return False, f"Missing required columns: {', '.join(missing_columns)}"

        # Validate that numeric columns contain valid data
        numeric_columns = ['value', 'count']  # Add other numeric columns as needed
        for col in numeric_columns:
            if col in df_columns:
                non_numeric = df[col].apply(lambda x: not pd.api.types.is_numeric_dtype(type(x)))
                if non_numeric.any():
                    return False, f"Column '{col}' contains non-numeric values"

        return True, "Valid file structure"

    def process_raw_data(self) -> pd.DataFrame:
        """Process raw security data from CSV and create grouped dataset."""
        try:
            print(f"Attempting to read: {self.raw_data_path}")
            print(f"File exists: {self.raw_data_path.exists()}")

            # Get raw data with validation and metadata extraction
            raw_df = self.get_raw_dataframe()
            self.db_handler.initialize_db_from_dataframe(raw_df)

            # Detect report type and set tree order if not provided
            if not self.tree_order:
                detected_types = self.security_handler.detect_report_type()
                if detected_types:
                    # Use most detailed report type available
                    report_type = detected_types[-1]
                    self.tree_order = self.security_handler.get_chart_fields(report_type)
                    print(f"Using most detailed report type available: {report_type}")
                    print(f"Tree order set to: {self.tree_order}")
                else:
                    raise ValueError("No valid report type detected")

            # Group by the tree order and count occurrences
            grouped_data = raw_df.groupby(self.tree_order).size().reset_index(name='Count')

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
                data=self.tree,
                tree_order=self.tree_order
            )

            # Save the result
            with open(self.sunburst_data_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(f"Data created and saved to {self.sunburst_data_path}")
            return metadata

        except Exception as e:
            print(f"Error creating data structure: {str(e)}")
            raise

    def get_raw_dataframe(self) -> pd.DataFrame:
        """Get the raw data from CSV with improved header detection and validation."""
        try:
            print(f"Reading raw data from: {self.raw_data_path}")

            # First read the metadata rows
            with open(self.raw_data_path, 'r', encoding='utf-8') as f:
                rows = []
                for _ in range(4):
                    rows.append(f.readline().strip())

                # Extract report type from first row, first cell
                self.report_type = rows[0].split(',')[0].strip('"')
                print(f"Extracted report type: {self.report_type}")

                # Extract and parse date span from second row
                date_span = rows[1].split(',')[0].strip('"')
                if ' - ' in date_span:
                    start_str, end_str = date_span.split(' - ')
                    start_str = start_str.strip().strip('"')
                    end_str = end_str.strip().strip('"')
                    try:
                        start_date = datetime.strptime(start_str, '%m/%d/%Y %H:%M')
                        end_date = datetime.strptime(end_str, '%m/%d/%Y %H:%M')
                        self.date_start = start_date.strftime('%b. %-d, %Y')
                        self.date_end = end_date.strftime('%b. %-d, %Y')
                    except ValueError as e:
                        print(f"Error parsing dates: {e}")
                        self.date_start = start_str
                        self.date_end = end_str

            # Now detect the actual data header row, starting after metadata
            header_row = 3  # Start checking after metadata rows
            with open(self.raw_data_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if i < header_row:
                        continue
                    # Look for a line containing common header terms
                    if any(term in line.lower() for term in ['incident', 'tag_name', 'hit_type']):
                        header_row = i
                        break
                    if i >= header_row + 7:  # Limit the search to 7 rows after metadata
                        break

            # Read the CSV with the detected header row
            df = pd.read_csv(self.raw_data_path, skiprows=header_row)

            # Clean column names
            df.columns = df.columns.str.lower().str.replace(' ', '_')

            # Validate the structure
            is_valid, error_message = self.validate_file_structure(df)
            if not is_valid:
                raise ValueError(error_message)

            print("\nColumns in raw data:", df.columns.tolist())
            return df

        except Exception as e:
            print(f"Error reading raw data: {str(e)}")
            raise

    def process_all(self) -> ReportMetadata:
        """Run the complete processing pipeline."""
        self.process_raw_data()
        return self.create_sunburst_data()

if __name__ == "__main__":
    processor = ReportProcessor("Sample", "sample_data.csv")
    processor.process_all()
