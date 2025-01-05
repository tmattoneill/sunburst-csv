import pandas as pd
import csv
import json
import sys
from typing import Dict, Optional, Tuple, List, TypedDict, Union
from pathlib import Path
from palettes import Palette


class TreeNode(TypedDict):
    """
    Represents a structure for a tree node with attributes for hierarchical data
    representation, including styling and nested child nodes.

    This data structure is commonly used in scenarios where a tree-like
    representation is required, such as in visualizations, graphs, or recursive
    data processing.

    :ivar name: The name or label associated with the tree node.
    :type name: str
    :ivar value: The numeric value related to the node, utilized for various
        calculations or visual significance.
    :type value: float
    :ivar itemStyle: A dictionary containing style-related properties for the
        node, defining its appearance in certain contexts.
    :type itemStyle: Dict[str, str]
    :ivar children: A list of child nodes, allowing the representation of nested
        tree structures.
    :type children: List['TreeNode']
    """
    name: str
    value: float
    itemStyle: Dict[str, str]
    children: List['TreeNode']


class TreeRoot(TypedDict):
    """
    Represents the root of a tree structure with a name, a value,
    and a list of child nodes.

    This class is used to define the structure of a tree root,
    containing a string name, a floating-point value, and
    references to its children nodes.

    :ivar name: The name of the tree root.
    :ivar value: The numeric value associated with the tree root.
    :ivar children: A list of child nodes connected to the tree root.
    """
    name: str
    value: float
    children: List[TreeNode]


class ReportProcessor:
    """
    A class to handle security data processing and visualization data creation.
    Combines raw data processing and sunburst chart JSON generation.
    """

    def __init__(self, base_path: str = "../data", palette_name: str = "ocean"):
        """
        Initialize the processor with paths and configuration.

        Args:
            base_path: Base path for data files
            palette_name: Name of the color palette to use for visualization
        """
        self.base_path = Path(base_path)
        self.raw_data_path = self.base_path / "raw/raw_data_7_days.csv"
        self.processed_data_path = self.base_path / "dataset.csv"
        self.sunburst_data_path = self.base_path / "sunburst_data.json"

        # Initialize color palette
        self.palette = Palette(palette_name)

        # Initialize the tree structure
        self.tree: Union[TreeRoot, Dict] = {}

    def set_palette(self, palette_name: str) -> None:
        """
        Change the color palette.

        Args:
            palette_name: Name of the palette to use
        """
        self.palette.set_palette(palette_name)

    @staticmethod
    def _set_csv_field_limit() -> None:
        """Set up CSV field size limit to handle large fields."""
        max_int = sys.maxsize
        while True:
            try:
                csv.field_size_limit(max_int)
                break
            except OverflowError:
                max_int = int(max_int/10)

    def process_raw_data(self) -> pd.DataFrame:
        """
        Process raw security data from CSV and create grouped dataset.

        Returns:
            DataFrame containing processed data
        """
        try:
            # Read the input CSV file
            df = pd.read_csv(self.raw_data_path)

            # Group by the requested columns and count occurrences
            grouped_data = df.groupby([
                'Expected Behavior',
                'Provider Account',
                'Publisher Name',
                'Malware Condition'
            ]).size().reset_index(name='Count')

            # Sort by count in descending order
            grouped_data = grouped_data.sort_values('Count', ascending=False)

            # Save to CSV file
            grouped_data.to_csv(self.processed_data_path, index=False)
            print(f"Processing complete. Data saved to '{self.processed_data_path}'")

            return grouped_data

        except FileNotFoundError:
            print(f"Error: Input file '{self.raw_data_path}' not found")
            raise
        except Exception as e:
            print(f"An error occurred during raw data processing: {str(e)}")
            raise

    @staticmethod
    def _process_row(row: list) -> Tuple[Optional[str], Optional[List[str]], Optional[float]]:
        """
        Process a single CSV row for the sunburst chart.

        Args:
            row: A list of values from the CSV

        Returns:
            tuple containing:
                - key: The top level parent (first non-empty value)
                - path: List of node names leading to the value
                - value: The numeric value for this path
        """
        # Clean the row - remove empty strings and whitespace
        cleaned_row = [str(item).strip() for item in row if item and str(item).strip()]

        if not cleaned_row:
            return None, None, None

        # Find the first non-empty value for key and collect path until we hit a number
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
        """
        Update the JSON tree with a new path and value.

        Args:
            path: List of node names leading to value
            value: Value to add at the leaf
        """
        # Initialize if this is the first entry
        if not self.tree:
            self.tree = TreeRoot(
                name='zMaticoo',
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
            # Create new top-level node with next color from palette
            color_idx = len(self.tree['children'])
            top_node = TreeNode(
                name=top_name,
                value=value,
                itemStyle={'color': self.palette[color_idx]},
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
                # Create new node with proper typing
                next_node = TreeNode(
                    name=name,
                    value=value,
                    itemStyle={'color': top_node['itemStyle']['color']},
                    children=[]
                )
                current['children'].append(next_node)
            else:
                next_node['value'] += value

            current = next_node

    def create_sunburst_data(self, skip_header: bool = False) -> TreeRoot:
        """
        Create sunburst chart data from processed CSV.

        Args:
            skip_header: Whether to skip the first row of the CSV

        Returns:
            Dictionary containing the sunburst chart data
        """
        try:
            # Reset the tree
            self.tree = {}

            # Process the CSV one row at a time
            with open(self.processed_data_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                if skip_header:
                    next(reader)

                for row in reader:
                    try:
                        key, path, value = self._process_row(row)
                        if key and path and value is not None:
                            self._update_json_tree(path, value)
                    except Exception as e:
                        print(f"Warning: Error processing row {row}: {str(e)}")
                        continue

            # Save the result
            with open(self.sunburst_data_path, 'w', encoding='utf-8') as f:
                json.dump(self.tree, f, indent=2, ensure_ascii=False)

            print(f"Sunburst data created and saved to {self.sunburst_data_path}")
            return self.tree

        except Exception as e:
            print(f"Error creating sunburst data: {str(e)}")
            raise

    def process_all(self, palette_name: Optional[str] = None) -> TreeRoot:
        """
        Run the complete processing pipeline: raw data → processed CSV → sunburst JSON.

        Args:
            palette_name: Optional name of palette to use for this processing run

        Returns:
            Dictionary containing the final sunburst chart data
        """
        if palette_name:
            self.set_palette(palette_name)
        self.process_raw_data()
        return self.create_sunburst_data()


if __name__ == "__main__":
    # Example usage with different palettes
    processor = ReportProcessor()

    # Process with default ocean palette
    processor.process_all()

    # Process with a different palette
    processor.process_all("sunset")