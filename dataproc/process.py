import csv
import json
from typing import Dict, Any
import sys

def process_row(row: list) -> tuple[str, list, float]:
    """
    Process a single CSV row, returning the key (top level parent), path, and value.
    Handles arbitrary length rows and values at any position.

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
    path = []
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

def update_json_tree(tree: Dict[str, Any], path: list, value: float, colors: list) -> None:
    """
    Update the JSON tree with a new path and value.

    Args:
        tree: Current JSON tree structure
        path: List of node names leading to value
        value: Value to add at the leaf
        colors: List of colors for styling
    """
    # Initialize if this is the first entry
    if 'name' not in tree:
        tree.update({
            'name': 'zMaticoo',
            'value': 0,
            'children': []
        })

    # Update root value
    tree['value'] += value

    # Find or create top-level node
    top_name = path[0]
    top_node = None
    for child in tree['children']:
        if child['name'] == top_name:
            top_node = child
            break

    if top_node is None:
        # Create new top-level node with next color
        color_idx = len(tree['children']) % len(colors)
        top_node = {
            'name': top_name,
            'value': value,
            'itemStyle': {'color': colors[color_idx]},
            'children': []
        }
        tree['children'].append(top_node)
    else:
        top_node['value'] += value

    # Process remaining path elements
    current = top_node
    for i, name in enumerate(path[1:], 1):
        # Look for existing node
        next_node = None
        if 'children' in current:
            for child in current['children']:
                if child['name'] == name:
                    next_node = child
                    break

        if next_node is None:
            # Create new node
            next_node = {
                'name': name,
                'value': value,
                'itemStyle': {'color': top_node['itemStyle']['color']}
            }
            if i < len(path) - 1:  # Not the last element
                next_node['children'] = []
            if 'children' not in current:
                current['children'] = []
            current['children'].append(next_node)
        else:
            next_node['value'] += value

        current = next_node

def create_sunburst_json(input_path: str, output_path: str, skip_header: bool = False) -> None:
    """
    Create a sunburst chart JSON from CSV data, processing one row at a time.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output JSON file
        skip_header: Whether to skip the first row of the CSV (default: False)
    """
    # Increase CSV field size limit for long rows
    maxInt = sys.maxsize
    while True:
        try:
            csv.field_size_limit(maxInt)
            break
        except OverflowError:
            maxInt = int(maxInt/10)

    # Define colors for first level
    colors = [
        '#03045e', '#0077b6', '#00b4d8', '#90e0ef', '#023e8a',
        '#0096c7', '#48cae4', '#ade8f4', '#caf0f8', '#014f86'
    ]

    # Initialize the tree
    tree = {}

    # Process the CSV one row at a time
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, quoting=csv.QUOTE_MINIMAL)
            if skip_header:
                next(reader)  # Skip header only if requested

            for row in reader:
                try:
                    key, path, value = process_row(row)
                    if key and path and value is not None:
                        update_json_tree(tree, path, value, colors)
                except Exception as e:
                    print(f"Warning: Error processing row {row}: {str(e)}")
                    continue

        # Save the result
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)

        print(f"Data processed and saved to {output_path}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    create_sunburst_json('../data/dataset.csv', '../data/sunburst_data.json', skip_header=False)