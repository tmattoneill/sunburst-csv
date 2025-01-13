import sqlite3
from contextlib import contextmanager
import pandas as pd
from typing import Dict, Any
from pathlib import Path


class DatabaseHandler:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        # Create a new connection for each request
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize_db_from_dataframe(self, df: pd.DataFrame):
        """Initialize the database directly from a pandas DataFrame."""
        try:
            print("Initializing database from DataFrame")
            print(f"Columns being stored: {df.columns.tolist()}")

            # Create and populate the database
            with self.get_connection() as conn:
                # Clear existing table
                conn.execute("DROP TABLE IF EXISTS security_data")

                # Create new table from DataFrame
                df.to_sql('security_data', conn, index=False)

                print(f"Loaded {len(df)} rows into database")

                return df.columns.tolist()

        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise

    def initialize_db(self, dataset_path: str = "../data/dataset.csv"):
        """Initialize the database with the processed dataset."""
        try:
            # Read the processed dataset
            df = pd.read_csv(dataset_path)
            print(f"Loading data from {dataset_path}")
            print(f"Columns found: {df.columns.tolist()}")

            # Create and populate the database
            with self.get_connection() as conn:
                # Clear existing table
                conn.execute("DROP TABLE IF EXISTS security_data")

                # Create new table from DataFrame
                df.to_sql('security_data', conn, index=False)
                conn.commit()

                print(f"Loaded {len(df)} rows into database")

            return df.columns.tolist()

        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            raise

    def get_all_data(self,
                     page: int = 1,
                     items_per_page: int = 20) -> Dict[str, Any]:
        """Get all data with pagination."""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get total count
                cursor.execute("SELECT COUNT(*) FROM security_data")
                total_items = cursor.fetchone()[0]

                # Get paginated data
                offset = (page - 1) * items_per_page
                cursor.execute(
                    "SELECT * FROM security_data LIMIT ? OFFSET ?",
                    (items_per_page, offset)
                )
                data = [dict(row) for row in cursor.fetchall()]

                return {
                    "data": data,
                    "total": total_items,
                    "page": page,
                    "total_pages": (total_items + items_per_page - 1) // items_per_page
                }

        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            raise