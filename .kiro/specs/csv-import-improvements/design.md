# Design Document: CSV Import Improvements

## Overview

This design implements a multi-step import wizard that guides users through configuring CSV/Excel imports with intelligent defaults and flexible overrides. The system will detect file structure, infer data types, and allow customization while maintaining backward compatibility with existing security report workflows.

## Architecture

### High-Level Flow

```
Upload File → File Analysis → Import Wizard → Data Processing → Visualization
     ↓              ↓              ↓                ↓                ↓
  Storage      Detection      User Config      Transform         Display
```

### Component Architecture

```
Frontend (Vue 3)
├── FileUploadModal (existing, enhanced)
├── ImportWizard (new)
│   ├── Step1: Header Selection
│   ├── Step2: Data Type Configuration
│   └── Step3: Display Names & Review
├── TemplateManager (new)
└── Enhanced visualizations (use display names)

Backend (Flask)
├── /api/upload (existing, enhanced)
├── /api/analyze (new) - File structure analysis
├── /api/configure-import (new) - Save import config
├── /api/process-import (new) - Execute import with config
├── /api/templates (new) - CRUD for import templates
└── dataproc/
    ├── file_analyzer.py (new)
    ├── type_detector.py (new)
    ├── data_transformer.py (new)
    └── import_config.py (new)
```

## Components and Interfaces

### 1. File Analyzer (Backend)

**Purpose:** Analyze uploaded files to detect structure and provide preview data.

**Class: `FileAnalyzer`**

```python
class FileAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df_preview = None
        
    def analyze(self) -> AnalysisResult:
        """
        Analyze file structure and return preview data.
        
        Returns:
            AnalysisResult with:
            - preview_rows: First 10 rows as list of lists
            - suggested_header_row: int (best guess)
            - file_type: 'security_report' | 'generic_csv'
            - row_count: total rows in file
            - encoding: detected encoding
        """
        
    def detect_header_row(self) -> int:
        """
        Heuristic detection of header row:
        - Look for row with all non-empty, unique values
        - Check if next row has different data types
        - Score each row and return best candidate
        """
        
    def detect_security_report(self) -> bool:
        """
        Check if file matches security report format:
        - Row 0 contains report type keywords
        - Row 1 contains date range pattern
        - Row 3 is empty or metadata
        - Row 4 contains expected column names
        """
```

**API Endpoint: `/api/analyze`**

```
POST /api/analyze
Body: { "filePath": "uploaded-file.csv" }

Response: {
  "preview_rows": [
    ["Title Row", "", ""],
    ["", "", ""],
    ["Name", "Value", "Date"],
    ["Widget A", "100", "2025-01-01"],
    ...
  ],
  "suggested_header_row": 2,
  "file_type": "generic_csv",
  "row_count": 1500,
  "encoding": "utf-8",
  "is_security_report": false
}
```

### 2. Type Detector (Backend)

**Purpose:** Analyze column data and detect/convert types.

**Class: `TypeDetector`**

```python
class TypeDetector:
    SUPPORTED_TYPES = ['text', 'integer', 'float', 'percentage', 
                       'currency', 'date', 'boolean']
    
    def detect_column_type(self, values: List[str], 
                          sample_size: int = 100) -> TypeInfo:
        """
        Analyze sample values and detect type.
        
        Returns:
            TypeInfo with:
            - detected_type: str
            - confidence: float (0-1)
            - conversion_success_rate: float
            - sample_values: list of original values
            - converted_samples: list of converted values
            - ambiguous: bool (if multiple types possible)
        """
        
    def convert_value(self, value: str, target_type: str) -> Any:
        """Convert single value to target type."""
        
    def detect_percentage(self, value: str) -> Optional[float]:
        """Detect and convert percentage formats."""
        
    def detect_currency(self, value: str) -> Optional[float]:
        """Detect and convert currency formats."""
        
    def detect_date(self, value: str) -> Optional[datetime]:
        """Detect and convert date formats."""
```

**API Endpoint: `/api/detect-types`**

```
POST /api/detect-types
Body: {
  "filePath": "uploaded-file.csv",
  "headerRow": 2,
  "columns": ["Name", "Value", "Date"]
}

Response: {
  "columns": [
    {
      "name": "Name",
      "detected_type": "text",
      "confidence": 1.0,
      "samples": ["Widget A", "Widget B", "Widget C"]
    },
    {
      "name": "Value",
      "detected_type": "currency",
      "confidence": 0.95,
      "samples": ["$100.00", "$250.50", "$1,000.00"],
      "converted_samples": [100.00, 250.50, 1000.00],
      "ambiguous": false
    },
    {
      "name": "Date",
      "detected_type": "date",
      "confidence": 0.85,
      "samples": ["2025-01-01", "01/15/2025", "2025-02-20"],
      "converted_samples": ["2025-01-01", "2025-01-15", "2025-02-20"],
      "ambiguous": true,
      "possible_formats": ["ISO", "US", "ISO"]
    }
  ]
}
```

### 3. Display Name Generator (Backend)

**Purpose:** Generate human-readable column names.

**Class: `DisplayNameGenerator`**

```python
class DisplayNameGenerator:
    ACRONYMS = ['id', 'url', 'api', 'html', 'css', 'sql', 'csv']
    COMMON_PREFIXES = ['col_', 'field_', 'data_', 'val_']
    COMMON_SUFFIXES = ['_id', '_key', '_field', '_col']
    
    def generate(self, technical_name: str) -> str:
        """
        Generate display name from technical name.
        
        Examples:
        - "num_widgets" → "Num Widgets"
        - "totalRevenue" → "Total Revenue"
        - "col_customer_id" → "Customer ID"
        - "api_endpoint_url" → "API Endpoint URL"
        """
        
    def to_title_case(self, text: str) -> str:
        """Convert to title case with acronym handling."""
        
    def remove_affixes(self, text: str) -> str:
        """Remove common prefixes and suffixes."""
```

### 4. Import Configuration (Backend)

**Purpose:** Store and manage import configurations.

**Class: `ImportConfig`**

```python
@dataclass
class ImportConfig:
    file_name: str
    header_row: int
    column_mappings: List[ColumnMapping]
    skip_rows: List[int]
    template_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
@dataclass
class ColumnMapping:
    original_name: str
    display_name: str
    data_type: str
    conversion_rules: Dict[str, Any]
    
class ImportConfigManager:
    def save_template(self, config: ImportConfig) -> str:
        """Save config as reusable template."""
        
    def load_template(self, template_name: str) -> ImportConfig:
        """Load saved template."""
        
    def match_template(self, file_structure: Dict) -> Optional[str]:
        """Find matching template for file structure."""
        
    def list_templates(self) -> List[Dict]:
        """List all saved templates."""
```

**Storage:** JSON files in `backend/data/import_templates/`

### 5. Data Transformer (Backend)

**Purpose:** Apply import configuration to transform raw data.

**Class: `DataTransformer`**

```python
class DataTransformer:
    def __init__(self, config: ImportConfig):
        self.config = config
        self.type_detector = TypeDetector()
        self.errors = []
        
    def transform(self, file_path: str) -> TransformResult:
        """
        Apply configuration and transform data.
        
        Returns:
            TransformResult with:
            - dataframe: transformed pandas DataFrame
            - errors: list of conversion errors
            - stats: transformation statistics
            - audit_log: detailed change log
        """
        
    def apply_column_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rename columns and apply display names."""
        
    def apply_type_conversions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert data types according to config."""
        
    def handle_conversion_errors(self, errors: List[ConversionError]) -> None:
        """Log and handle conversion failures."""
```

### 6. Import Wizard (Frontend)

**Purpose:** Multi-step UI for configuring imports.

**Component: `ImportWizard.vue`**

```vue
<template>
  <div class="import-wizard">
    <WizardProgress :current-step="currentStep" :total-steps="3" />
    
    <Step1HeaderSelection 
      v-if="currentStep === 1"
      :preview-rows="previewRows"
      :suggested-row="suggestedHeaderRow"
      @select="handleHeaderSelection"
    />
    
    <Step2TypeConfiguration
      v-if="currentStep === 2"
      :columns="columns"
      :type-info="typeInfo"
      @configure="handleTypeConfiguration"
    />
    
    <Step3DisplayNames
      v-if="currentStep === 3"
      :columns="columns"
      :suggested-names="suggestedNames"
      @finalize="handleFinalize"
    />
  </div>
</template>
```

**Step 1: Header Selection**
- Display first 10 rows in a table
- Highlight suggested header row
- Allow user to click any row to select as header
- Show validation warnings if selected row seems invalid
- "Skip to automatic processing" button for security reports

**Step 2: Type Configuration**
- Show each column with:
  - Original name
  - Detected type (with confidence indicator)
  - Sample values (original and converted)
  - Dropdown to override type
  - Conversion error handling options
- Bulk actions: "Accept all suggestions", "Set all to text"
- Preview of how data will look after conversion

**Step 3: Display Names & Review**
- Editable table with:
  - Original name (read-only)
  - Display name (editable)
  - Data type (from step 2)
  - Sample converted values
- "Save as template" checkbox and name input
- Final review summary:
  - X rows will be imported
  - Y columns configured
  - Z conversions will be applied
- "Import" button to proceed

## Data Models

### Database Schema Extensions

**New Table: `import_configs`**
```sql
CREATE TABLE import_configs (
    id INTEGER PRIMARY KEY,
    template_name TEXT UNIQUE,
    file_pattern TEXT,  -- regex or glob pattern
    header_row INTEGER,
    config_json TEXT,  -- JSON blob of full config
    created_at TIMESTAMP,
    last_used TIMESTAMP,
    use_count INTEGER DEFAULT 0
);
```

**New Table: `import_audit_log`**
```sql
CREATE TABLE import_audit_log (
    id INTEGER PRIMARY KEY,
    import_id TEXT,
    file_name TEXT,
    config_used TEXT,  -- template name or 'custom'
    rows_processed INTEGER,
    rows_failed INTEGER,
    transformations_applied TEXT,  -- JSON array
    created_at TIMESTAMP
);
```

### API Data Structures

**ImportConfiguration**
```typescript
interface ImportConfiguration {
  fileName: string;
  headerRow: number;
  columns: ColumnConfig[];
  skipRows?: number[];
  templateName?: string;
}

interface ColumnConfig {
  originalName: string;
  displayName: string;
  dataType: 'text' | 'integer' | 'float' | 'percentage' | 
            'currency' | 'date' | 'boolean';
  conversionRules?: {
    dateFormat?: string;
    currencySymbol?: string;
    decimalPlaces?: number;
    onError?: 'null' | 'keep_original' | 'exclude_row';
  };
}
```

## Error Handling (CRITICAL - ALWAYS FAIL GRACEFULLY)

### Guiding Principles
1. **Never show technical errors to users** - Translate to plain language
2. **Always explain what happened and why** - Context matters
3. **Always provide actionable next steps** - Tell users what to do
4. **Preserve user work** - Don't lose their configuration on errors
5. **Log everything server-side** - For debugging without exposing to users

### Error Categories and User Messages

#### 1. File Upload Errors

**Error:** File too large (> 100MB)
```
❌ File Too Large
Your file is 150MB, but the maximum size is 100MB.

What you can do:
• Split your file into smaller chunks
• Remove unnecessary columns before uploading
• Contact support if you need to import large datasets regularly
```

**Error:** Unsupported file type
```
❌ Unsupported File Type
We can only import CSV, XLS, and XLSX files.
Your file appears to be: [detected type]

What you can do:
• Save your file as CSV or Excel format
• Check that the file extension matches the content
```

**Error:** Corrupted file
```
❌ Unable to Read File
The file appears to be corrupted or in an unexpected format.

What you can do:
• Try opening the file in Excel/Numbers to verify it's valid
• Re-export the file from your source system
• Try uploading a different file
```

**Error:** Encoding issues
```
❌ Character Encoding Issue
We had trouble reading some characters in your file.
Detected encoding: [encoding]

What you can do:
• Save your file with UTF-8 encoding
• We'll try to read it anyway - click "Continue" to proceed
• Some special characters may not display correctly
```

#### 2. Header Detection Errors

**Error:** No valid header row found
```
⚠️ Couldn't Find Column Headers
We looked at the first 10 rows but couldn't identify which row contains your column names.

What you can do:
• Manually select the row with your column headers below
• If your file has no headers, we'll use "Column 1", "Column 2", etc.
```

**Error:** Duplicate column names
```
⚠️ Duplicate Column Names Found
Row 3 has duplicate column names: "Value" appears 3 times

What you can do:
• Select a different header row
• We can auto-rename them: "Value", "Value_2", "Value_3"
• Edit your file to use unique column names
```

**Error:** Empty column names
```
⚠️ Some Columns Have No Names
Row 2 has 3 empty column names

What you can do:
• Select a different header row
• We can auto-name them: "Column_A", "Column_B", "Column_C"
```

#### 3. Type Detection Errors

**Error:** Ambiguous date format
```
⚠️ Date Format Unclear
Column "Date" has dates in multiple formats:
• "01/02/2025" - Could be Jan 2 or Feb 1
• "2025-03-15" - ISO format
• "March 20, 2025" - Text format

What you can do:
• Tell us which format to use: [US] [European] [ISO]
• We'll convert all dates to that format
• Dates that don't match will be flagged
```

**Error:** Mixed data types
```
⚠️ Mixed Data Types in Column
Column "Amount" contains:
• 85% numbers: $100, $250, $1,000
• 15% text: "N/A", "Pending", "TBD"

What you can do:
• Convert to numbers and replace text with blank: [Recommended]
• Keep everything as text
• Exclude rows with text values (15 rows)
```

**Error:** Conversion failures
```
⚠️ Some Values Couldn't Be Converted
Column "Percentage" - 12 values failed to convert:
• Row 45: "N/A" → Can't convert to number
• Row 67: "100%" → Converted to 1.0 ✓
• Row 89: "invalid" → Can't convert to number

What you can do:
• Replace failed values with blank [Recommended]
• Keep original text for failed values
• Exclude rows with failed conversions (12 rows)

[View All Errors]
```

#### 4. Import Processing Errors

**Error:** Database error
```
❌ Import Failed
We couldn't save your data due to a technical issue.
Error ID: #12345 (for support reference)

What you can do:
• Try importing again - your configuration is saved
• Check if you have enough disk space
• Contact support with Error ID #12345
```

**Error:** Timeout
```
⚠️ Import Taking Longer Than Expected
Your file has 50,000 rows and is still processing...

What you can do:
• Wait a bit longer - we're still working on it
• Cancel and try with a smaller file
• We'll email you when it's done (if you provide email)
```

**Error:** Partial import success
```
⚠️ Import Completed with Warnings
Successfully imported: 9,850 rows
Failed to import: 150 rows

Common issues:
• 100 rows had invalid dates
• 50 rows had missing required values

What you can do:
• View the data that was imported
• Download error report to see which rows failed
• Fix the issues and re-import just the failed rows
```

#### 5. Template Errors

**Error:** Template doesn't match file
```
⚠️ Template Mismatch
Template "Sales Report" expects these columns:
✓ Date, ✓ Amount, ✓ Customer
✗ Region (missing in your file)

What you can do:
• Continue without the template
• Modify the template to match your file
• Add the missing column to your file
```

**Error:** Template save failed
```
❌ Couldn't Save Template
Template name "Q1 Report" already exists.

What you can do:
• Choose a different name
• Overwrite the existing template
• View existing templates
```

### Error Response Structure

**Backend API Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_COLUMNS",
    "message": "Duplicate column names found in header row",
    "user_message": "Row 3 has duplicate column names: 'Value' appears 3 times",
    "details": {
      "row": 3,
      "duplicates": ["Value", "Value", "Value"],
      "positions": [2, 5, 8]
    },
    "suggestions": [
      "Select a different header row",
      "Auto-rename duplicates",
      "Edit file to use unique names"
    ],
    "recoverable": true,
    "error_id": "ERR-2025-04-10-12345"
  }
}
```

**Frontend Error Display Component:**
```vue
<ErrorMessage
  :type="error.code"
  :title="error.user_message"
  :suggestions="error.suggestions"
  :recoverable="error.recoverable"
  @retry="handleRetry"
  @cancel="handleCancel"
/>
```

### Conversion Errors
- **Strategy:** Collect all errors during transformation
- **User Options:**
  - Replace with null (default for numeric types)
  - Keep original text value
  - Exclude entire row
- **Logging:** Store in audit log with row number and original value
- **User Message:** Show count, samples, and clear options

### File Format Errors
- **Invalid encoding:** Attempt multiple encodings, show user-friendly message with suggestions
- **Corrupted file:** Explain what's wrong, suggest fixes
- **Too large:** Show size limit, suggest alternatives

### Template Matching Errors
- **Column mismatch:** Show visual diff, offer to continue anyway
- **Type mismatch:** Warn but allow override with explanation
- **Missing columns:** Highlight missing, allow partial match with warning

### Progress and Feedback
- Show progress bars for long operations
- Provide cancel option for long-running imports
- Show estimated time remaining
- Confirm successful completion with statistics

## Testing Strategy

### Unit Tests
- `FileAnalyzer`: Test header detection with various file structures
- `TypeDetector`: Test each type conversion with edge cases
- `DisplayNameGenerator`: Test name generation rules
- `DataTransformer`: Test transformation pipeline with errors

### Integration Tests
- End-to-end import flow with sample files
- Template save/load/apply workflow
- Backward compatibility with security reports
- Error handling scenarios

### User Acceptance Tests
- Import wizard usability testing
- Template reuse workflow
- Error recovery scenarios
- Performance with large files

## Performance Considerations

### File Analysis
- Read only first 10 rows for preview (fast)
- Sample 100 rows per column for type detection (configurable)
- Stream large files instead of loading entirely into memory

### Type Detection
- Cache detection results per column
- Parallel processing for multiple columns
- Lazy evaluation: only detect when user views step 2

### Frontend Performance
- Virtualized table for large preview data
- Debounced input for display name editing
- Progressive loading of type detection results

## Security Considerations

- **File Upload:** Validate file size, type, and scan for malicious content
- **Template Storage:** Sanitize template names, prevent path traversal
- **SQL Injection:** Use parameterized queries for all database operations
- **XSS:** Sanitize all user-provided display names before rendering

## Migration Strategy

### Phase 1: Add New Features (Non-Breaking)
- Deploy new endpoints alongside existing ones
- Add import wizard as optional flow
- Maintain existing security report auto-processing

### Phase 2: User Adoption
- Show "Try new import wizard" banner for generic CSVs
- Collect feedback and iterate
- Build template library for common formats

### Phase 3: Deprecation (Optional)
- If new flow proves superior, gradually migrate security reports
- Provide migration tool for existing workflows
- Maintain backward compatibility for 6 months

## Open Questions

1. **Date Format Ambiguity:** How to handle "01/02/2025" (US vs EU)?
   - **Proposal:** Ask user to select region/format preference
   
2. **Large File Handling:** What's the size limit before we require streaming?
   - **Proposal:** 100MB threshold, show progress bar for larger files
   
3. **Template Sharing:** Should users be able to export/share templates?
   - **Proposal:** Yes, as JSON files for team collaboration
   
4. **Undo Functionality:** Should users be able to undo an import?
   - **Proposal:** Keep original file, allow re-import with different config
   
5. **Column Ordering:** Should users be able to reorder columns?
   - **Proposal:** Phase 2 feature, not critical for MVP
