# Implementation Plan: CSV Import Improvements

## Task Overview

This implementation plan breaks down the CSV import improvements into incremental, testable tasks. Each task builds on previous work and can be validated independently.

---

## Phase 1: Backend Foundation

### Task 1: File Analysis Infrastructure

- [ ] 1.1 Create `backend/app/dataproc/file_analyzer.py`
  - Implement `FileAnalyzer` class with file reading and preview generation
  - Add header row detection heuristics (check for unique non-empty values, type consistency in following rows)
  - Add security report format detection logic
  - _Requirements: 1.1, 1.4, 1.5, 4.1, 4.2_

- [ ] 1.2 Create `/api/analyze` endpoint in `routes.py`
  - Accept file path from previous upload
  - Call `FileAnalyzer` to generate preview and suggestions
  - Return JSON with preview rows, suggested header, file type
  - Handle errors (file not found, encoding issues, corrupted files)
  - _Requirements: 1.1, 1.2, 4.1_

- [ ] 1.3 Add encoding detection and handling
  - Try UTF-8, then fallback to common encodings (latin-1, cp1252)
  - Return detected encoding in analysis response
  - Handle encoding errors gracefully
  - _Requirements: 1.1_

### Task 2: Type Detection System

- [ ] 2.1 Create `backend/app/dataproc/type_detector.py`
  - Implement `TypeDetector` class with type detection methods
  - Add percentage detection: regex for "X%", "X.Y%"
  - Add currency detection: regex for "$X", "€X", "£X" with comma separators
  - Add formatted number detection: "1,000", "1,000.00"
  - Add date detection: try common formats with dateutil parser
  - _Requirements: 2.1, 2.2_

- [ ] 2.2 Implement type conversion methods
  - `convert_percentage()`: strip %, divide by 100
  - `convert_currency()`: strip symbols and commas, parse float
  - `convert_number()`: remove commas, parse float/int
  - `convert_date()`: parse to ISO format string
  - Handle conversion failures with try/except, return None
  - _Requirements: 2.1, 2.2, 2.5_

- [ ] 2.3 Add column-level type detection
  - Sample first 100 rows of column (configurable)
  - Try each type detector, score by success rate
  - Return detected type with confidence score
  - Flag ambiguous cases (multiple types with similar scores)
  - _Requirements: 2.1, 2.3_

- [ ] 2.4 Create `/api/detect-types` endpoint
  - Accept file path, header row, column names
  - Use `TypeDetector` to analyze each column
  - Return type info with samples and converted examples
  - _Requirements: 2.1, 2.2, 2.3_

### Task 3: Display Name Generation

- [ ] 3.1 Create `backend/app/dataproc/display_name_generator.py`
  - Implement `DisplayNameGenerator` class
  - Add snake_case to Title Case conversion
  - Add camelCase to Title Case conversion
  - Add acronym detection and capitalization (ID, URL, API, etc.)
  - Remove common prefixes/suffixes (col_, _id, etc.)
  - _Requirements: 3.1_

- [ ] 3.2 Add display name suggestion to analysis
  - Generate display names for all detected columns
  - Return in `/api/analyze` response
  - _Requirements: 3.1, 3.2_

### Task 4: Import Configuration Management

- [ ] 4.1 Create `backend/app/dataproc/import_config.py`
  - Define `ImportConfig` and `ColumnMapping` dataclasses
  - Implement `ImportConfigManager` for template CRUD
  - Store templates as JSON files in `backend/data/import_templates/`
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 4.2 Create `/api/templates` CRUD endpoints
  - `GET /api/templates` - List all templates
  - `POST /api/templates` - Save new template
  - `GET /api/templates/:name` - Get specific template
  - `PUT /api/templates/:name` - Update template
  - `DELETE /api/templates/:name` - Delete template
  - _Requirements: 5.1, 5.4_

- [ ] 4.3 Add template matching logic
  - Compare file column names to template column names
  - Calculate similarity score
  - Return best matching template (if score > threshold)
  - _Requirements: 5.2, 5.3_

### Task 5: Data Transformation Engine

- [ ] 5.1 Create `backend/app/dataproc/data_transformer.py`
  - Implement `DataTransformer` class
  - Read file starting from configured header row
  - Apply column renaming (original → display names)
  - Apply type conversions per column configuration
  - _Requirements: 2.4, 2.5, 3.4_

- [ ] 5.2 Add error handling and logging
  - Collect conversion errors with row numbers
  - Apply user-selected error handling strategy (null, keep original, exclude row)
  - Generate audit log with transformation details
  - _Requirements: 2.4, 2.5_

- [ ] 5.3 Create `/api/process-import` endpoint
  - Accept file path and import configuration
  - Use `DataTransformer` to process file
  - Save transformed data to database
  - Return success status with statistics
  - _Requirements: 2.4, 2.5, 3.4_

- [ ] 5.4 Add import audit logging
  - Create `import_audit_log` table in database
  - Log each import with config used, rows processed, errors
  - Store transformation report for download
  - _Requirements: NFR: Data Integrity_

---

## Phase 2: Frontend Import Wizard

### Task 6: Import Wizard Shell

- [ ] 6.1 Create `frontend/src/components/ImportWizard.vue`
  - Multi-step wizard component with progress indicator
  - Navigation: Back, Next, Cancel buttons
  - State management for wizard data
  - _Requirements: 1.1, NFR: Usability_

- [ ] 6.2 Add wizard trigger to FileLoaderModal
  - After file upload, call `/api/analyze`
  - If generic CSV detected, show "Configure Import" button
  - If security report detected, show "Use Automatic Processing" option
  - _Requirements: 4.2_

- [ ] 6.3 Create wizard progress component
  - Visual step indicator (1/3, 2/3, 3/3)
  - Highlight current step
  - Show completed steps with checkmarks
  - _Requirements: NFR: Usability_

### Task 7: Step 1 - Header Selection

- [ ] 7.1 Create `Step1HeaderSelection.vue` component
  - Display first 10 rows in a table
  - Show row numbers (0-indexed)
  - Highlight suggested header row
  - Allow clicking any row to select as header
  - _Requirements: 1.1, 1.2, 1.3_

- [ ] 7.2 Add header validation
  - Check for empty values in selected row
  - Check for duplicate column names
  - Show warning if validation fails
  - Suggest alternative rows
  - _Requirements: 1.5, 1.6_

- [ ] 7.3 Add "Skip to automatic" option
  - Show button if security report detected
  - Bypass wizard and use existing processing
  - _Requirements: 4.1, 4.2_

### Task 8: Step 2 - Type Configuration

- [ ] 8.1 Create `Step2TypeConfiguration.vue` component
  - Display table with columns: Name, Type, Samples, Actions
  - Show detected type with confidence indicator
  - Show sample values (original and converted)
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 8.2 Add type override controls
  - Dropdown for each column to select type
  - Options: Text, Integer, Float, Percentage, Currency, Date, Boolean
  - Update converted samples when type changes
  - _Requirements: 2.3_

- [ ] 8.3 Add error handling configuration
  - For columns with conversion errors, show error count
  - Radio buttons: "Replace with null", "Keep as text", "Exclude rows"
  - Preview impact of each option
  - _Requirements: 2.4, 2.5_

- [ ] 8.4 Add bulk actions
  - "Accept all suggestions" button
  - "Set all to text" button (safe fallback)
  - "Reset to defaults" button
  - _Requirements: NFR: Usability_

### Task 9: Step 3 - Display Names & Review

- [ ] 9.1 Create `Step3DisplayNames.vue` component
  - Editable table: Original Name, Display Name, Type, Samples
  - Pre-fill with suggested display names
  - Allow inline editing of display names
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 9.2 Add display name validation
  - Check for empty display names
  - Warn on duplicate display names
  - Show validation errors inline
  - _Requirements: 3.3_

- [ ] 9.3 Add template save option
  - Checkbox: "Save as template for future imports"
  - Text input for template name
  - Validate template name (unique, no special chars)
  - _Requirements: 5.1_

- [ ] 9.4 Add final review summary
  - Show statistics: X rows, Y columns, Z conversions
  - List any warnings or errors
  - "Import" button to proceed
  - "Back" to revise configuration
  - _Requirements: NFR: Usability_

### Task 10: Template Management UI

- [ ] 10.1 Create `TemplateManager.vue` component
  - List all saved templates
  - Show template details: name, columns, last used
  - Actions: Edit, Delete, Export
  - _Requirements: 5.4_

- [ ] 10.2 Add template selection on upload
  - After file analysis, check for matching templates
  - Show "Apply template: [name]" button if match found
  - Allow user to modify before applying
  - _Requirements: 5.2, 5.3_

- [ ] 10.3 Add template import/export
  - Export template as JSON file
  - Import template from JSON file
  - Validate imported template structure
  - _Requirements: 5.4_

---

## Phase 3: Integration & Polish

### Task 11: Backward Compatibility

- [ ] 11.1 Update existing security report processing
  - Keep current auto-detection logic
  - Add option to use wizard instead
  - Ensure existing workflows unchanged
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 11.2 Add migration path for existing data
  - Allow re-importing with new wizard
  - Preserve original files for re-processing
  - _Requirements: 4.3_

### Task 12: Visualization Updates

- [ ] 12.1 Update DataTable component
  - Use display names in column headers
  - Keep original names in data structure
  - _Requirements: 3.4_

- [ ] 12.2 Update SunburstChart component
  - Use display names in labels
  - Show original names in tooltips
  - _Requirements: 3.4_

- [ ] 12.3 Update export functionality
  - Add option to export with display names or original names
  - Update CSV export headers
  - _Requirements: 3.5_

### Task 13: Error Handling & User Feedback (CRITICAL)

- [ ] 13.1 Create error message component
  - Build reusable `ErrorMessage.vue` component
  - Display error title, explanation, and suggestions
  - Show error icon and appropriate styling
  - Include "Retry", "Go Back", "Contact Support" actions
  - _Requirements: NFR: Error Handling_

- [ ] 13.2 Implement backend error translation
  - Create error code to user message mapping
  - Never expose stack traces or technical errors to users
  - Include actionable suggestions for each error type
  - Log full technical details server-side
  - Return structured error responses with user_message field
  - _Requirements: NFR: Error Handling_

- [ ] 13.3 Add file upload error handling
  - File too large: Show size limit and suggestions
  - Unsupported type: Explain supported formats
  - Corrupted file: Suggest fixes
  - Encoding issues: Offer to continue with warning
  - _Requirements: NFR: Error Handling_

- [ ] 13.4 Add header detection error handling
  - No valid headers: Offer manual selection or auto-naming
  - Duplicate columns: Offer auto-rename or manual fix
  - Empty columns: Offer auto-naming
  - _Requirements: NFR: Error Handling_

- [ ] 13.5 Add type detection error handling
  - Ambiguous dates: Ask user to specify format with examples
  - Mixed types: Show distribution and offer options
  - Conversion failures: Show count, samples, and recovery options
  - _Requirements: NFR: Error Handling_

- [ ] 13.6 Add import processing error handling
  - Database errors: Show error ID for support, offer retry
  - Timeout: Show progress, offer to wait or cancel
  - Partial success: Show what worked, what failed, offer error report
  - _Requirements: NFR: Error Handling_

- [ ] 13.7 Add template error handling
  - Template mismatch: Show visual diff, offer to continue
  - Save conflicts: Offer rename or overwrite
  - Load failures: Explain issue and suggest fixes
  - _Requirements: NFR: Error Handling_

- [ ] 13.8 Add loading states and progress
  - Show spinner during file analysis
  - Show progress bar during type detection
  - Show progress during import processing with cancel option
  - Show estimated time remaining for long operations
  - _Requirements: NFR: Performance, NFR: Error Handling_

- [ ] 13.9 Add success feedback
  - Show import success message with statistics
  - Offer to download transformation report
  - Show any warnings even on success
  - Auto-redirect to visualization after delay
  - _Requirements: NFR: Usability_

- [ ] 13.10 Preserve user work on errors
  - Save wizard state to localStorage
  - Restore configuration after error recovery
  - Don't lose user's display name edits
  - Allow resuming from where they left off
  - _Requirements: NFR: Error Handling_

### Task 14: Documentation & Help

- [ ] 14.1 Add inline help text
  - Tooltips for each configuration option
  - Examples of each data type
  - Explanation of error handling strategies
  - _Requirements: NFR: Usability_

- [ ] 14.2 Create user guide
  - Step-by-step import wizard guide
  - Template management guide
  - Troubleshooting common issues
  - _Requirements: NFR: Usability_

- [ ] 14.3 Add sample files
  - Provide example CSV files for testing
  - Include various formats (percentages, currency, dates)
  - Include problematic cases (mixed types, empty rows)
  - _Requirements: Testing_

---

## Phase 4: Testing & Optimization

### Task 15: Unit Tests

- [ ]* 15.1 Test FileAnalyzer
  - Test header detection with various file structures
  - Test security report detection
  - Test encoding detection
  - _Requirements: All Requirement 1_

- [ ]* 15.2 Test TypeDetector
  - Test each type conversion with edge cases
  - Test ambiguous type detection
  - Test error handling
  - _Requirements: All Requirement 2_

- [ ]* 15.3 Test DisplayNameGenerator
  - Test name generation rules
  - Test acronym handling
  - Test affix removal
  - _Requirements: All Requirement 3_

- [ ]* 15.4 Test DataTransformer
  - Test transformation pipeline
  - Test error collection and handling
  - Test audit log generation
  - _Requirements: All Requirement 2, 3_

### Task 16: Integration Tests

- [ ]* 16.1 Test end-to-end import flow
  - Upload → Analyze → Configure → Import → Visualize
  - Test with various file formats
  - Test error scenarios
  - _Requirements: All Requirements_

- [ ]* 16.2 Test template workflow
  - Save template → Apply to new file → Modify → Import
  - Test template matching
  - Test template CRUD operations
  - _Requirements: All Requirement 5_

- [ ]* 16.3 Test backward compatibility
  - Import security reports with old flow
  - Import security reports with new wizard
  - Verify identical results
  - _Requirements: All Requirement 4_

### Task 17: Performance Optimization

- [ ]* 17.1 Optimize file analysis
  - Profile preview generation
  - Implement streaming for large files
  - Add caching where appropriate
  - _Requirements: NFR: Performance_

- [ ]* 17.2 Optimize type detection
  - Profile type detection algorithms
  - Implement parallel processing for columns
  - Add lazy evaluation
  - _Requirements: NFR: Performance_

- [ ]* 17.3 Optimize frontend rendering
  - Implement virtual scrolling for large previews
  - Debounce user inputs
  - Lazy load type detection results
  - _Requirements: NFR: Performance_

---

## Notes

- Tasks marked with `*` are optional testing tasks
- Each task should be completed and tested before moving to the next
- Backend tasks (1-5) can be developed independently of frontend tasks (6-10)
- Phase 3 (11-14) requires both backend and frontend to be complete
- Phase 4 (15-17) is ongoing throughout development
