"""
File analyzer for CSV/Excel import preprocessing.
Handles file preview, header detection, and format analysis.
"""
import pandas as pd
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import chardet
import re
from datetime import datetime


class FileAnalyzer:
    """Analyzes uploaded files for structure and content."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.encoding = None
        self.preview_rows = []
        
    def analyze(self, num_rows: int = 10) -> Dict[str, Any]:
        """
        Analyze file structure and return preview data.
        
        Args:
            num_rows: Number of rows to preview (default 10)
            
        Returns:
            Dictionary with:
            - preview_rows: First N rows as list of lists
            - suggested_header_row: int (best guess)
            - file_type: 'security_report' | 'generic_csv'
            - row_count: total rows in file
            - encoding: detected encoding
            - error: error message if analysis failed
        """
        try:
            # Detect encoding
            self.encoding = self._detect_encoding()
            
            # Read preview rows
            self.preview_rows = self._read_preview_rows(num_rows)
            
            if not self.preview_rows:
                return {
                    "success": False,
                    "error": {
                        "code": "EMPTY_FILE",
                        "user_message": "The file appears to be empty or has no readable data.",
                        "suggestions": [
                            "Check that the file contains data",
                            "Try opening the file in Excel to verify it's valid",
                            "Try uploading a different file"
                        ]
                    }
                }
            
            # Detect if security report
            is_security_report = self._detect_security_report()
            
            # Suggest header row
            suggested_header = self._detect_header_row()
            
            # Count total rows (estimate for large files)
            row_count = self._count_rows()
            
            return {
                "success": True,
                "preview_rows": self.preview_rows,
                "suggested_header_row": suggested_header,
                "file_type": "security_report" if is_security_report else "generic_csv",
                "is_security_report": is_security_report,
                "row_count": row_count,
                "encoding": self.encoding
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "ANALYSIS_FAILED",
                    "user_message": f"Unable to analyze file: {str(e)}",
                    "suggestions": [
                        "Check that the file is a valid CSV or Excel file",
                        "Try opening the file in Excel to verify it's not corrupted",
                        "Try re-exporting the file from your source system"
                    ],
                    "technical_details": str(e)
                }
            }
    
    def _detect_encoding(self) -> str:
        """Detect file encoding."""
        try:
            with open(self.file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception:
            return 'utf-8'  # Default fallback
    
    def _read_preview_rows(self, num_rows: int) -> List[List[str]]:
        """Read first N rows from file."""
        rows = []
        
        try:
            # Try reading as CSV first
            with open(self.file_path, 'r', encoding=self.encoding, errors='replace') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i >= num_rows:
                        break
                    rows.append(row)
            
            return rows
            
        except Exception as e:
            # If CSV fails, try pandas (handles Excel)
            try:
                df = pd.read_excel(self.file_path, nrows=num_rows, header=None)
                return df.values.tolist()
            except Exception:
                raise Exception(f"Could not read file as CSV or Excel: {str(e)}")
    
    def _detect_header_row(self) -> int:
        """
        Heuristic detection of header row.
        Returns the row index (0-based) that is most likely the header.
        """
        if not self.preview_rows:
            return 0
        
        scores = []
        
        for idx, row in enumerate(self.preview_rows):
            score = 0
            
            # Skip empty rows
            if not any(cell for cell in row if cell):
                scores.append(0)
                continue
            
            # Check if all values are non-empty
            non_empty = sum(1 for cell in row if cell and str(cell).strip())
            if non_empty == len(row):
                score += 3
            
            # Check if values are unique (good indicator of headers)
            unique_ratio = len(set(row)) / len(row) if row else 0
            score += unique_ratio * 5
            
            # Check if next row has different characteristics (data vs headers)
            if idx < len(self.preview_rows) - 1:
                next_row = self.preview_rows[idx + 1]
                # If current row is text and next row has numbers, likely header
                current_has_numbers = any(self._is_numeric(cell) for cell in row)
                next_has_numbers = any(self._is_numeric(cell) for cell in next_row)
                
                if not current_has_numbers and next_has_numbers:
                    score += 4
            
            # Penalize rows that look like titles (single cell, all caps, etc.)
            if len([c for c in row if c]) == 1:
                score -= 2
            
            if any(str(cell).isupper() and len(str(cell)) > 20 for cell in row):
                score -= 1
            
            scores.append(score)
        
        # Return index of highest scoring row
        if scores:
            return scores.index(max(scores))
        return 0
    
    def _detect_security_report(self) -> bool:
        """
        Check if file matches security report format.
        Expected format:
        - Row 0: Report type
        - Row 1: Date range
        - Row 2: Empty or metadata
        - Row 3: Column headers
        """
        if len(self.preview_rows) < 4:
            return False
        
        try:
            # Check row 0 for report type keywords
            row0_text = ' '.join(str(cell) for cell in self.preview_rows[0]).lower()
            report_keywords = ['report', 'security', 'incident', 'threat', 'scan']
            has_report_keyword = any(keyword in row0_text for keyword in report_keywords)
            
            # Check row 1 for date range pattern (MM/DD/YYYY - MM/DD/YYYY)
            row1_text = ' '.join(str(cell) for cell in self.preview_rows[1])
            has_date_range = bool(re.search(r'\d{1,2}/\d{1,2}/\d{4}.*-.*\d{1,2}/\d{1,2}/\d{4}', row1_text))
            
            # Check row 3 for expected column names
            row3_text = ' '.join(str(cell) for cell in self.preview_rows[3]).lower()
            expected_columns = ['incident', 'tag', 'hit', 'scan']
            has_expected_columns = sum(1 for col in expected_columns if col in row3_text) >= 2
            
            return has_report_keyword and has_date_range and has_expected_columns
            
        except Exception:
            return False
    
    def _count_rows(self) -> int:
        """Count total rows in file (with reasonable limit for performance)."""
        try:
            count = 0
            with open(self.file_path, 'r', encoding=self.encoding, errors='replace') as f:
                for _ in f:
                    count += 1
                    if count > 100000:  # Cap at 100k for performance
                        return count
            return count
        except Exception:
            return len(self.preview_rows)  # Fallback to preview count
    
    @staticmethod
    def _is_numeric(value: Any) -> bool:
        """Check if value is numeric."""
        try:
            float(str(value).replace(',', '').replace('$', '').replace('%', ''))
            return True
        except (ValueError, AttributeError):
            return False
