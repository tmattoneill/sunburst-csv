import pandas as pd
import json
import csv
from typing import Dict, Any

def process_row(row: list) -> tuple[str, list, float]:
    """
    Process a single CSV row, returning the key (top level parent), path, and value.

    Args:
        row: A list of values from the CSV

    Returns:
        tuple containing:
            - key: The top level parent (first non-empty value)
            - path: List of node names leading to the value
            - value: The numeric value for this path
    """
    # Strip empty values from end of row
    while row and not row[-1]:
        row.pop()

    if not row:
        return None, None, None

    # Find the first non-empty value (key) and build path until we hit a number
    path = []
    value = None
    key = None

    for item in row:
        if not item:  # Skip empty values
            continue

        # Try to convert to float
        try:
            value = float(item)
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
            'name': 'Root',
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

def create_sunburst_json(input_path: str, output_path: str) -> None:
    """
    Create a sunburst chart JSON from CSV data, processing one row at a time.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output JSON file
    """
    # Define colors for first level
    colors = [
        '#2f4554', '#c23531', '#d48265', '#91c7ae', '#749f83',
        '#ca8622', '#bda29a', '#6e7074', '#546570', '#c4ccd3'
    ]

    # Initialize the tree
    tree = {}

    # Process the CSV one row at a time
    with open(input_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header

        for row in reader:
            key, path, value = process_row(row)
            if key and path and value is not None:
                update_json_tree(tree, path, value, colors)

    # Save the result
    with open(output_path, 'w') as f:
        json.dump(tree, f, indent=2)

if __name__ == "__main__":
    try:
        create_sunburst_json('../data/dataset.csv', '../data/sunburst_data.json')
        print("Data processed and saved to ../data/sunburst_data.json")
    except Exception as e:
        print(f"Error: {str(e)}")