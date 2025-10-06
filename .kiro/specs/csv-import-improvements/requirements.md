# Requirements Document: CSV Import Improvements

## Introduction

This feature enhances the CSV/Excel import process to handle real-world data files more intelligently. Currently, the system expects a very specific format (security incident reports with metadata rows). This enhancement will make the import process flexible, user-guided, and intelligent about data types, while maintaining backward compatibility with existing security report workflows.

## Requirements

### Requirement 1: Flexible Header Row Detection

**User Story:** As a user uploading CSV files with varying structures, I want the system to help me identify where my actual data begins, so that I don't have to manually clean my files before upload.

#### Acceptance Criteria

1. WHEN a file is uploaded THEN the system SHALL read the first 10 rows and present them to the user for review
2. WHEN displaying preview rows THEN the system SHALL show row numbers (0-indexed or 1-indexed, to be decided) alongside the raw content
3. WHEN the user selects a header row THEN the system SHALL use that row as column names and begin data import from the next row
4. IF the system detects a likely header row automatically THEN it SHALL pre-select that row but allow user override
5. WHEN a header row is selected THEN the system SHALL validate that it contains reasonable column names (non-empty, unique values)
6. IF the selected row appears invalid as headers THEN the system SHALL warn the user and suggest alternatives

### Requirement 2: Intelligent Data Type Detection and Conversion

**User Story:** As a user importing financial or statistical data, I want percentages, currency, and formatted numbers to be recognized as numeric values, so that I can perform calculations and visualizations correctly.

#### Acceptance Criteria

1. WHEN parsing cell values THEN the system SHALL detect and convert common numeric formats:
   - Percentages: "3%", "15.5%" → 0.03, 0.155
   - Currency: "$1,000.00", "€500", "£1,234.56" → 1000.00, 500, 1234.56
   - Formatted numbers: "1,000", "1,000.00" → 1000, 1000.00
   - Negative numbers: "(100)", "-100" → -100, -100

2. WHEN parsing cell values THEN the system SHALL detect and convert common date formats:
   - ISO dates: "2025-04-10", "2025-04-10T14:30:00"
   - US dates: "04/10/2025", "4/10/25"
   - EU dates: "10/04/2025", "10.04.2025"
   - Text dates: "April 10, 2025", "10 Apr 2025"

3. WHEN data type detection is ambiguous THEN the system SHALL present options to the user for clarification

4. WHEN a column contains mixed types THEN the system SHALL:
   - Attempt to convert all values to the most common type
   - Flag rows that fail conversion
   - Allow user to choose: keep as text, force conversion (with nulls for failures), or exclude problematic rows

5. WHEN conversion fails for a value THEN the system SHALL log the failure and either:
   - Replace with null/empty (if user chose force conversion)
   - Keep original text value (if user chose keep as text)
   - Exclude the row (if user chose exclude)

### Requirement 3: User-Friendly Column Display Names

**User Story:** As a user working with technical column names, I want to provide human-readable display names, so that my charts and tables are more presentable and understandable.

#### Acceptance Criteria

1. WHEN column headers are detected THEN the system SHALL generate suggested display names by:
   - Converting snake_case to Title Case: "num_widgets" → "Num Widgets"
   - Converting camelCase to Title Case: "numWidgets" → "Num Widgets"
   - Removing common prefixes/suffixes: "col_name", "name_field" → "Name"
   - Capitalizing acronyms: "id", "url", "api" → "ID", "URL", "API"

2. WHEN presenting column configuration THEN the system SHALL show:
   - Original column name (technical name)
   - Suggested display name (editable)
   - Detected data type
   - Sample values from the column

3. WHEN the user edits a display name THEN the system SHALL:
   - Validate it's not empty
   - Warn if duplicate display names exist
   - Store the mapping for use in UI components

4. WHEN generating visualizations or tables THEN the system SHALL use display names in user-facing elements while maintaining original names in data structures

5. WHEN exporting data THEN the system SHALL allow user to choose between original names or display names for column headers

### Requirement 4: Backward Compatibility with Security Reports

**User Story:** As an existing user with security incident reports, I want the new import process to still work with my existing file format, so that I don't have to change my workflow.

#### Acceptance Criteria

1. WHEN a file matches the security report format THEN the system SHALL automatically:
   - Detect the report type from row 1
   - Extract date range from row 2
   - Use row 4 as headers
   - Skip the new import wizard

2. WHEN automatic detection is uncertain THEN the system SHALL offer the user a choice:
   - "This looks like a security report. Use automatic processing?"
   - "This looks like a generic CSV. Use import wizard?"

3. WHEN processing a security report THEN the system SHALL maintain existing behavior for:
   - Report type detection
   - Tree structure generation
   - Database schema
   - Visualization logic

### Requirement 5: Import Configuration Persistence

**User Story:** As a user who regularly imports similar files, I want to save my import configuration, so that I don't have to reconfigure the same settings every time.

#### Acceptance Criteria

1. WHEN completing an import configuration THEN the system SHALL offer to save it as a template with a user-provided name

2. WHEN uploading a new file THEN the system SHALL:
   - Check if a saved template matches the file structure
   - Offer to apply the template automatically
   - Allow user to modify template settings before applying

3. WHEN a template is applied THEN the system SHALL:
   - Use saved header row selection
   - Apply saved data type conversions
   - Use saved display name mappings
   - Validate that column names match (warn if mismatches exist)

4. WHEN managing templates THEN the user SHALL be able to:
   - List all saved templates
   - Edit template settings
   - Delete templates
   - Export/import templates as JSON

## Non-Functional Requirements

### Performance
- File preview (first 10 rows) SHALL load within 2 seconds for files up to 100MB
- Data type detection SHALL process within 5 seconds for files up to 10,000 rows
- Full import SHALL provide progress feedback for files taking longer than 10 seconds

### Usability
- Import wizard SHALL be completable in 3 steps or fewer for simple cases
- Each step SHALL have clear "Back" and "Next" navigation
- Help text SHALL be available for each configuration option
- Preview data SHALL be visible at each step to provide context

### Data Integrity
- Original uploaded file SHALL be preserved unchanged
- All transformations SHALL be logged for audit purposes
- User SHALL be able to download a transformation report showing what was changed

### Accessibility
- Import wizard SHALL be keyboard navigable
- Screen readers SHALL be able to announce all configuration options
- Color SHALL not be the only indicator of data type or validation status

### Error Handling (CRITICAL)
- **ALL errors SHALL fail gracefully with helpful, actionable messages**
- Error messages SHALL include:
  - What went wrong (in plain language)
  - Why it happened (if known)
  - What the user can do to fix it
  - Example of correct format (when applicable)
- Error messages SHALL NEVER show:
  - Stack traces to end users
  - Technical jargon without explanation
  - Generic "An error occurred" messages
- WHEN an error occurs THEN the system SHALL:
  - Log technical details server-side for debugging
  - Show user-friendly message to the user
  - Preserve user's work (don't lose configuration)
  - Offer recovery options (retry, go back, contact support)
- WHEN multiple errors occur THEN the system SHALL:
  - Group related errors
  - Prioritize critical errors first
  - Show summary with option to view details
- WHEN an error is recoverable THEN the system SHALL:
  - Suggest specific fix
  - Offer to auto-fix if possible
  - Allow user to continue with partial success
