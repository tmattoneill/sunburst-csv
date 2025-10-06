"""
Type detection and conversion for CSV columns.
Handles percentages, currency, dates, and formatted numbers.
"""
import re
import pandas as pd
from typing import Any, Optional, Dict, List
from datetime import datetime
from dateutil import parser as date_parser


class TypeDetector:
    """Detects and converts data types in CSV columns."""
    
    SUPPORTED_TYPES = ['text', 'numeric', 'currency', 'percentage', 'date']
    
    # Currency symbols to detect
    CURRENCY_SYMBOLS = ['$', '€', '£', '¥', '₹', '₽', '₩', '₪', '₦', '₱', '₡', '₴']
    CURRENCY_PATTERN = re.compile(r'[' + ''.join(re.escape(s) for s in CURRENCY_SYMBOLS) + r']')
    
    def detect_column_type(self, values: pd.Series, sample_size: int = 100) -> Dict[str, Any]:
        """
        Analyze column values and detect type.
        
        Args:
            values: Pandas Series of column values
            sample_size: Number of values to sample for detection
            
        Returns:
            Dictionary with:
            - detected_type: str
            - confidence: float (0-1)
            - sample_values: list of original values
            - converted_samples: list of converted values
            - ambiguous: bool
        """
        # Get non-null sample
        sample = values.dropna().head(sample_size)
        
        if len(sample) == 0:
            return {
                'detected_type': 'text',
                'confidence': 0.0,
                'sample_values': [],
                'converted_samples': [],
                'ambiguous': False
            }
        
        sample_list = sample.tolist()
        
        # Try each type detector in order of specificity
        # Percentage (most specific)
        pct_result = self._detect_percentage(sample_list)
        if pct_result['confidence'] > 0.8:
            return pct_result
        
        # Currency
        curr_result = self._detect_currency(sample_list)
        if curr_result['confidence'] > 0.8:
            return curr_result
        
        # Date
        date_result = self._detect_date(sample_list)
        if date_result['confidence'] > 0.8:
            return date_result
        
        # Numeric (formatted numbers)
        num_result = self._detect_numeric(sample_list)
        if num_result['confidence'] > 0.8:
            return num_result
        
        # Default to text
        return {
            'detected_type': 'text',
            'confidence': 1.0,
            'sample_values': sample_list[:5],
            'converted_samples': sample_list[:5],
            'ambiguous': False
        }
    
    def _detect_percentage(self, values: List[Any]) -> Dict[str, Any]:
        """Detect if column contains percentages."""
        pct_count = 0
        converted = []
        
        for val in values:
            val_str = str(val).strip()
            if '%' in val_str:
                pct_count += 1
                converted_val = self.convert_percentage(val_str)
                converted.append(converted_val if converted_val is not None else val)
            else:
                converted.append(val)
        
        confidence = pct_count / len(values) if values else 0.0
        
        return {
            'detected_type': 'percentage',
            'confidence': confidence,
            'sample_values': values[:5],
            'converted_samples': converted[:5],
            'ambiguous': False
        }
    
    def _detect_currency(self, values: List[Any]) -> Dict[str, Any]:
        """Detect if column contains currency values."""
        curr_count = 0
        converted = []
        
        for val in values:
            val_str = str(val).strip()
            if self.CURRENCY_PATTERN.search(val_str):
                curr_count += 1
                converted_val = self.convert_currency(val_str)
                converted.append(converted_val if converted_val is not None else val)
            else:
                converted.append(val)
        
        confidence = curr_count / len(values) if values else 0.0
        
        return {
            'detected_type': 'currency',
            'confidence': confidence,
            'sample_values': values[:5],
            'converted_samples': converted[:5],
            'ambiguous': False
        }
    
    def _detect_date(self, values: List[Any]) -> Dict[str, Any]:
        """Detect if column contains dates."""
        date_count = 0
        converted = []
        formats_found = set()
        
        for val in values:
            val_str = str(val).strip()
            converted_val, date_format = self.convert_date(val_str)
            if converted_val is not None:
                date_count += 1
                converted.append(converted_val)
                if date_format:
                    formats_found.add(date_format)
            else:
                converted.append(val)
        
        confidence = date_count / len(values) if values else 0.0
        ambiguous = len(formats_found) > 1  # Multiple date formats detected
        
        return {
            'detected_type': 'date',
            'confidence': confidence,
            'sample_values': values[:5],
            'converted_samples': converted[:5],
            'ambiguous': ambiguous,
            'formats_found': list(formats_found) if ambiguous else []
        }
    
    def _detect_numeric(self, values: List[Any]) -> Dict[str, Any]:
        """Detect if column contains numeric values (including formatted)."""
        num_count = 0
        converted = []
        
        for val in values:
            converted_val = self.convert_number(val)
            if converted_val is not None:
                num_count += 1
                converted.append(converted_val)
            else:
                converted.append(val)
        
        confidence = num_count / len(values) if values else 0.0
        
        return {
            'detected_type': 'numeric',
            'confidence': confidence,
            'sample_values': values[:5],
            'converted_samples': converted[:5],
            'ambiguous': False
        }
    
    @staticmethod
    def convert_percentage(value: Any) -> Optional[float]:
        """
        Convert percentage string to decimal.
        Examples: "3%" -> 0.03, "15.5%" -> 0.155
        """
        try:
            val_str = str(value).strip()
            # Remove % sign
            val_str = val_str.replace('%', '').strip()
            # Remove commas
            val_str = val_str.replace(',', '')
            # Convert to float and divide by 100
            return float(val_str) / 100.0
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def convert_currency(value: Any) -> Optional[float]:
        """
        Convert currency string to number.
        Examples: "$1,000.00" -> 1000.0, "€500" -> 500.0
        """
        try:
            val_str = str(value).strip()
            # Remove currency symbols
            for symbol in TypeDetector.CURRENCY_SYMBOLS:
                val_str = val_str.replace(symbol, '')
            # Remove commas
            val_str = val_str.replace(',', '')
            # Remove spaces
            val_str = val_str.strip()
            # Convert to float
            return float(val_str)
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def convert_number(value: Any) -> Optional[float]:
        """
        Convert formatted number string to float.
        Examples: "1,000" -> 1000.0, "1,000.00" -> 1000.0
        """
        try:
            # If already a number, return it
            if isinstance(value, (int, float)):
                return float(value)
            
            val_str = str(value).strip()
            
            # Skip if it contains letters (except e for scientific notation)
            if re.search(r'[a-df-zA-DF-Z]', val_str):
                return None
            
            # Remove commas
            val_str = val_str.replace(',', '')
            # Remove spaces
            val_str = val_str.strip()
            # Convert to float
            return float(val_str)
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def convert_date(value: Any) -> tuple[Optional[str], Optional[str]]:
        """
        Convert date string to ISO format.
        Returns: (converted_date, format_detected)
        Examples: "2025-01-01" -> ("2025-01-01", "ISO")
                  "01/15/2025" -> ("2025-01-15", "US")
        """
        try:
            val_str = str(value).strip()
            
            # Try to parse with dateutil
            parsed_date = date_parser.parse(val_str, fuzzy=False)
            iso_date = parsed_date.strftime('%Y-%m-%d')
            
            # Detect format
            date_format = "ISO"
            if '/' in val_str:
                # Check if US (MM/DD/YYYY) or EU (DD/MM/YYYY)
                parts = val_str.split('/')
                if len(parts) == 3:
                    if int(parts[0]) > 12:
                        date_format = "EU"
                    else:
                        date_format = "US"  # Ambiguous, default to US
            elif '-' in val_str:
                date_format = "ISO"
            else:
                date_format = "TEXT"
            
            return iso_date, date_format
            
        except (ValueError, AttributeError, date_parser.ParserError):
            return None, None
    
    def convert_value(self, value: Any, target_type: str) -> Any:
        """
        Convert a single value to the target type.
        
        Args:
            value: Value to convert
            target_type: One of SUPPORTED_TYPES
            
        Returns:
            Converted value or None if conversion fails
        """
        if target_type == 'percentage':
            return self.convert_percentage(value)
        elif target_type == 'currency':
            return self.convert_currency(value)
        elif target_type == 'numeric':
            return self.convert_number(value)
        elif target_type == 'date':
            result, _ = self.convert_date(value)
            return result
        else:  # text
            return str(value) if value is not None else None
