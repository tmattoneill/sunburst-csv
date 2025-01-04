import pandas as pd

def process_security_data():
    try:
        # Read the input CSV file
        df = pd.read_csv('../data/raw_data_7_days.csv')

        # Group by the requested columns and count occurrences
        grouped_data = df.groupby([
            'Provider Account',
            'Publisher Name',
            'Expected Behavior',
            'Malware Condition'
        ]).size().reset_index(name='Count')

        # Sort by count in descending order
        grouped_data = grouped_data.sort_values('Count', ascending=False)

        # Save to CSV file
        grouped_data.to_csv('../data/dataset.csv', index=False)
        print("Processing complete. Data saved to '../data/dataset.csv'")

        # Display first few rows as preview
        print("\nFirst few rows of processed data:")
        print(grouped_data.head().to_string())

    except FileNotFoundError:
        print("Error: Input file '../data/raw_data_7_days.csv' not found")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    process_security_data()