"""
Display name generator for column names.
Converts technical names to human-readable format.
"""
import re
from typing import List


class DisplayNameGenerator:
    """Generates human-readable display names from technical column names."""
    
    # Common acronyms that should be uppercase
    ACRONYMS = ['id', 'url', 'api', 'html', 'css', 'sql', 'csv', 'json', 'xml',
                'http', 'https', 'ftp', 'ssh', 'ip', 'dns', 'cdn', 'seo', 'roi',
                'kpi', 'ctr', 'cpc', 'cpm', 'crm', 'erp', 'saas', 'b2b', 'b2c']
    
    # Common prefixes to remove
    COMMON_PREFIXES = ['col_', 'field_', 'data_', 'val_', 'value_', 'attr_', 
                       'prop_', 'item_', 'row_', 'column_']
    
    # Common suffixes to remove
    COMMON_SUFFIXES = ['_id', '_key', '_field', '_col', '_column', '_value',
                       '_data', '_attr', '_prop', '_item']
    
    @classmethod
    def generate(cls, technical_name: str) -> str:
        """
        Generate display name from technical name.
        
        Examples:
        - "num_widgets" → "Num Widgets"
        - "totalRevenue" → "Total Revenue"
        - "col_customer_id" → "Customer ID"
        - "api_endpoint_url" → "API Endpoint URL"
        - "dsp_name" → "DSP Name"
        
        Args:
            technical_name: Original column name
            
        Returns:
            Human-readable display name
        """
        if not technical_name:
            return ""
        
        # Start with the original name
        result = technical_name.strip()
        
        # Remove common prefixes
        result = cls._remove_affixes(result)
        
        # Convert to title case (handles both snake_case and camelCase)
        result = cls._to_title_case(result)
        
        # Handle acronyms
        result = cls._capitalize_acronyms(result)
        
        return result
    
    @classmethod
    def _remove_affixes(cls, text: str) -> str:
        """Remove common prefixes and suffixes."""
        # Remove prefixes
        for prefix in cls.COMMON_PREFIXES:
            if text.lower().startswith(prefix):
                text = text[len(prefix):]
                break
        
        # Remove suffixes
        for suffix in cls.COMMON_SUFFIXES:
            if text.lower().endswith(suffix):
                text = text[:-len(suffix)]
                break
        
        return text
    
    @classmethod
    def _to_title_case(cls, text: str) -> str:
        """
        Convert to title case, handling both snake_case and camelCase.
        """
        # Handle snake_case: replace underscores with spaces
        if '_' in text:
            text = text.replace('_', ' ')
        
        # Handle camelCase: insert space before capital letters
        # But preserve consecutive capitals (like "API" or "URL")
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
        
        # Title case each word
        words = text.split()
        result = ' '.join(word.capitalize() for word in words)
        
        return result
    
    @classmethod
    def _capitalize_acronyms(cls, text: str) -> str:
        """Capitalize known acronyms."""
        words = text.split()
        result = []
        
        for word in words:
            if word.lower() in cls.ACRONYMS:
                result.append(word.upper())
            else:
                result.append(word)
        
        return ' '.join(result)
    
    @classmethod
    def generate_batch(cls, technical_names: List[str]) -> dict:
        """
        Generate display names for multiple columns.
        
        Args:
            technical_names: List of technical column names
            
        Returns:
            Dictionary mapping technical names to display names
        """
        return {name: cls.generate(name) for name in technical_names}
