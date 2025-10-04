"""
Generic Sunburst Data Processor

Processes any CSV/XLSX file with hierarchical data into sunburst visualization format.
No hardcoded column assumptions - fully user-configurable.
"""

import pandas as pd
import json
import re
from typing import Dict, List, TypedDict, Union, Tuple
from pathlib import Path
import os


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


class ChartMetadata(TypedDict):
    """Metadata for the generic chart."""
    chart_name: str
    tree_order: List[str]
    value_column: str
    data: TreeRoot


class GenericProcessor:
    """
    Generic processor for creating sunburst visualizations from any hierarchical CSV data.

    Unlike the security-specific ReportProcessor, this class:
    - Accepts any CSV/XLSX without metadata row requirements
    - Uses user-selected columns for hierarchy and values
    - Aggregates numeric values instead of counting unique tags
    - No hardcoded column names or report types
    """

    def __init__(self,
                 input_file: str,
                 chart_name: str,
                 tree_order: List[str],
                 value_column: str,
                 data_path: str = "../data",
                 session_id: str = "default",
                 progress_callback=None):
        """
        Initialize the generic processor.

        Args:
            input_file: Name of CSV/XLSX file in data/raw/
            chart_name: User-provided name for the visualization
            tree_order: List of column names forming the hierarchy (e.g., ['dsp_name', 'brand_name', 'buyer_name'])
            value_column: Column name containing numeric values to aggregate (e.g., 'ad_spend')
            data_path: Base path for data storage
            session_id: Session identifier for multi-user support
            progress_callback: Optional callback function for progress updates
        """
        self.data_path = Path(os.getenv('DATA_PATH', data_path))
        self.raw_data_path = self.data_path / "raw" / input_file
        self.sunburst_data_path = self.data_path / f"{session_id}_sunburst_data.json"

        self.chart_name = chart_name
        self.tree_order = tree_order
        self.value_column = value_column
        self.tree: Union[TreeRoot, Dict] = {}
        self.session_id = session_id
        self.progress_callback = progress_callback

        # Validate inputs
        if not tree_order or len(tree_order) < 3:
            raise ValueError("tree_order must contain at least 3 column names")
        if not value_column:
            raise ValueError("value_column is required")
        if not chart_name:
            raise ValueError("chart_name is required")

    def _report_progress(self, current: int, total: int, message: str):
        """Report progress if callback is set."""
        if self.progress_callback:
            self.progress_callback(current, total, message)

    @staticmethod
    def clean_numeric_value(value: str) -> float:
        """
        Clean and convert a value to numeric, handling currency symbols, commas, etc.

        Examples:
            "$54,500.02" -> 54500.02
            "1,234.56" -> 1234.56
            "2.5%" -> 2.5
        """
        if pd.isna(value):
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        # Convert to string and clean
        value_str = str(value).strip()

        # Remove currency symbols
        value_str = re.sub(r'[$€£¥₹]', '', value_str)

        # Remove commas
        value_str = value_str.replace(',', '')

        # Handle percentages (keep the number, don't convert to decimal)
        value_str = value_str.replace('%', '')

        # Remove whitespace
        value_str = value_str.strip()

        try:
            return float(value_str)
        except (ValueError, AttributeError):
            return 0.0

    def read_dataframe(self) -> pd.DataFrame:
        """
        Read CSV or Excel file without any metadata row assumptions.
        Directly reads the data with headers in first row.
        """
        if not self.raw_data_path.exists():
            raise FileNotFoundError(f"Input file not found: {self.raw_data_path}")

        # Determine file type and read accordingly
        file_ext = self.raw_data_path.suffix.lower()

        if file_ext == '.csv':
            df = pd.read_csv(self.raw_data_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(self.raw_data_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        print(f"Read {len(df)} rows from {self.raw_data_path.name}")
        print(f"Columns: {df.columns.tolist()}")

        return df

    def validate_and_prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate that required columns exist and prepare data for processing.

        Args:
            df: Raw dataframe

        Returns:
            Cleaned and validated dataframe

        Raises:
            ValueError: If required columns are missing or data is invalid
        """
        # Check that all required columns exist
        all_columns = set(df.columns)
        required_columns = set(self.tree_order + [self.value_column])
        missing_columns = required_columns - all_columns

        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        # Create a copy to avoid modifying original
        df_clean = df.copy()

        # Clean the value column - handle currency and formatting
        print(f"Cleaning value column: {self.value_column}")
        df_clean[self.value_column] = df_clean[self.value_column].apply(self.clean_numeric_value)

        # Remove rows where value is 0 or NaN
        initial_count = len(df_clean)
        df_clean = df_clean[df_clean[self.value_column] > 0]
        removed_count = initial_count - len(df_clean)
        if removed_count > 0:
            print(f"Removed {removed_count} rows with zero or invalid values")

        # Remove rows with NaN in any hierarchy column
        initial_count = len(df_clean)
        df_clean = df_clean.dropna(subset=self.tree_order)
        removed_count = initial_count - len(df_clean)
        if removed_count > 0:
            print(f"Removed {removed_count} rows with missing hierarchy values")

        # Convert hierarchy columns to strings and strip whitespace
        for col in self.tree_order:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            # Remove rows with empty strings
            df_clean = df_clean[df_clean[col] != '']

        if len(df_clean) == 0:
            raise ValueError("No valid data remaining after cleaning")

        print(f"Validated data: {len(df_clean)} rows ready for processing")
        return df_clean

    def build_tree_recursive(self, df: pd.DataFrame, level: int = 0, level0_idx: int = 0, level0_total: int = 0) -> List[TreeNode]:
        """
        Recursively build tree structure from grouped data with progress tracking.

        Args:
            df: Dataframe subset for this level
            level: Current hierarchy level (0-indexed)
            level0_idx: For level 0, the current category index (for progress)
            level0_total: For level 0, total number of categories (for progress)

        Returns:
            List of TreeNode dictionaries
        """
        if level >= len(self.tree_order):
            return []

        col = self.tree_order[level]
        children = []
        unique_values = df[col].unique()

        # Group by current level column
        for idx, value in enumerate(unique_values):
            subset = df[df[col] == value]

            # Only report progress at the first level
            if level == 0:
                progress_pct = 20 + int((idx / len(unique_values)) * 70)  # 20-90%
                self._report_progress(
                    progress_pct,
                    100,
                    f"Processing {col}: {value} ({idx + 1}/{len(unique_values)})"
                )

            # Sum the value column for this node
            node_value = subset[self.value_column].sum()

            # Recursively build children
            child_nodes = self.build_tree_recursive(subset, level + 1)

            child = {
                'name': str(value),
                'value': float(node_value),
                'children': child_nodes
            }
            children.append(child)

        # Sort by value descending
        children.sort(key=lambda x: x['value'], reverse=True)

        return children

    def create_sunburst_data(self) -> ChartMetadata:
        """
        Create hierarchical sunburst data structure from CSV.

        Returns:
            ChartMetadata with tree structure
        """
        try:
            # Read and validate data
            self._report_progress(0, 100, "Reading file...")
            df = self.read_dataframe()

            self._report_progress(10, 100, "Validating data...")
            df = self.validate_and_prepare_data(df)

            # Build tree structure
            self._report_progress(20, 100, "Building tree structure...")
            print("Building tree structure...")
            total_value = df[self.value_column].sum()
            children = self.build_tree_recursive(df, level=0)

            self._report_progress(90, 100, "Finalizing...")
            self.tree = {
                'name': self.chart_name,
                'value': float(total_value),
                'children': children
            }

            # Create metadata object
            metadata = {
                'chart_name': self.chart_name,
                'tree_order': self.tree_order,
                'value_column': self.value_column,
                'source_file': str(self.raw_data_path.name),  # Store source file name for table queries
                'data': self.tree
            }

            # Save to JSON
            with open(self.sunburst_data_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self._report_progress(100, 100, "Complete!")
            print(f"✓ Sunburst data created and saved to {self.sunburst_data_path}")
            print(f"  Total value: {total_value:,.2f}")
            print(f"  Top-level categories: {len(children)}")

            return metadata

        except Exception as e:
            print(f"Error creating sunburst data: {str(e)}")
            raise

    def process_all(self):
        """
        Main processing pipeline - create sunburst visualization data.
        """
        print(f"\n{'='*60}")
        print(f"Processing: {self.chart_name}")
        print(f"Hierarchy: {' → '.join(self.tree_order)}")
        print(f"Value column: {self.value_column}")
        print(f"{'='*60}\n")

        self.create_sunburst_data()
        print("\n✓ Processing complete!")


def analyze_columns(file_path: Path) -> List[Dict]:
    """
    Analyze columns in a CSV/XLSX file to determine types and suitability.

    Args:
        file_path: Path to CSV or XLSX file

    Returns:
        List of column metadata dictionaries
    """
    # Read file
    file_ext = file_path.suffix.lower()
    if file_ext == '.csv':
        df = pd.read_csv(file_path, nrows=1000)  # Sample first 1000 rows
    elif file_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, nrows=1000)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

    columns_info = []

    for col in df.columns:
        series = df[col].dropna()

        if len(series) == 0:
            col_type = 'empty'
            suitable_for_value = False
            sample_value = None
        else:
            # Try to detect if numeric
            # Clean values and attempt conversion
            cleaned_values = series.apply(GenericProcessor.clean_numeric_value)
            numeric_ratio = (cleaned_values != 0).sum() / len(series)

            if numeric_ratio > 0.8:  # 80%+ can be converted to numeric
                col_type = 'numeric'
                suitable_for_value = True
                sample_value = series.iloc[0]
            else:
                col_type = 'text'
                suitable_for_value = False
                sample_value = str(series.iloc[0])[:50]  # Truncate long samples

        columns_info.append({
            'name': col,
            'type': col_type,
            'sample': str(sample_value) if sample_value is not None else None,
            'unique_count': int(df[col].nunique()),
            'suitable_for_value': suitable_for_value
        })

    return columns_info


def validate_column_selection(file_path: Path, tree_order: List[str], value_column: str) -> Tuple[bool, List[str]]:
    """
    Validate user's column selection before processing.

    Args:
        file_path: Path to data file
        tree_order: Selected hierarchy columns
        value_column: Selected value column

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []

    # Read file
    try:
        file_ext = file_path.suffix.lower()
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            errors.append(f"Unsupported file type: {file_ext}")
            return False, errors
    except Exception as e:
        errors.append(f"Failed to read file: {str(e)}")
        return False, errors

    # Check column count
    if len(tree_order) < 3:
        errors.append("Hierarchy must have at least 3 levels")

    # Check columns exist
    all_columns = set(df.columns)
    required = set(tree_order + [value_column])
    missing = required - all_columns
    if missing:
        errors.append(f"Columns not found in file: {', '.join(missing)}")
        return False, errors

    # Check for duplicates
    if value_column in tree_order:
        errors.append(f"Value column '{value_column}' cannot also be in hierarchy")

    if len(tree_order) != len(set(tree_order)):
        errors.append("Hierarchy columns must be unique (no duplicates)")

    # Check value column is numeric
    cleaned_values = df[value_column].apply(GenericProcessor.clean_numeric_value)
    numeric_ratio = (cleaned_values != 0).sum() / len(df)
    if numeric_ratio < 0.5:
        errors.append(f"Value column '{value_column}' must contain mostly numeric data (only {numeric_ratio*100:.1f}% valid)")

    # Check hierarchy columns have sufficient variety
    for col in tree_order:
        unique_count = df[col].nunique()
        if unique_count < 2:
            errors.append(f"Hierarchy column '{col}' must have at least 2 unique values (found {unique_count})")

    # Check we have enough data
    if len(df) < 10:
        errors.append(f"File must contain at least 10 rows (found {len(df)})")

    return len(errors) == 0, errors
