# Detailed Plan: CSV Import Improvements

## Overview
Implement three major enhancements to CSV import: (1) handle files with title/empty rows before headers, (2) improve numeric type detection (percentages, currency, dates), and (3) add optional display names for columns.

---

## PART 1: Header Row Detection & Selection

### UX Flow
Add **Step 1.5: "Verify Headers"** between file upload and hierarchy configuration:
- Display first 15 rows of raw file in a table with row numbers (0-14)
- Pre-select row 0 as default (current behavior - backwards compatible)
- User can click different row to select as header
- Optional "Skip rows before header" input (e.g., skip 2 title rows, then row 3 is header)
- Visual highlight of selected header row
- "Looks good, use this header" button to proceed

### Backend Changes

**New endpoint: `GET /api/file-preview`**
- Parameters: `filePath`, `numRows` (default 15)
- Returns: Array of arrays (raw rows, no header interpretation)
- Example: `[[row0], [row1], ...]`

**Modify `/api/file-info`**
- Add parameter: `headerRow` (default 0)
- Add parameter: `skipRows` (default 0)
- Use: `pd.read_csv(path, header=headerRow, skiprows=range(skipRows))`

**Modify `/api/process`**
- Accept `headerRow` and `skipRows` in request body
- Pass to `GenericProcessor.__init__`
- Store in metadata JSON for future reference

**generic_processor.py changes:**
- Add `header_row` and `skip_rows` to `__init__` parameters
- Modify `read_dataframe()`:
  ```python
  if file_ext == '.csv':
      skiprows = list(range(self.skip_rows)) if self.skip_rows > 0 else None
      df = pd.read_csv(self.raw_data_path, header=self.header_row, skiprows=skiprows)
  ```

### Frontend Changes

**FileLoaderModal.vue:**
- Add new step between steps 0 and 1: "Verify Headers"
- Update `stepTitles`: `['Upload File', 'Verify Headers', 'Configure Hierarchy', 'Select Value Column', 'Name & Create']`
- Add state: `headerRow = ref(0)`, `skipRows = ref(0)`, `rawPreview = ref([])`
- New method: `fetchRawPreview()` - calls `/api/file-preview`
- New UI section for Step 1 (new numbering):
  - Table showing raw rows with selectable row numbers
  - Input for "Skip rows"
  - Highlight selected header row in blue
- Pass `headerRow` and `skipRows` to all subsequent API calls

---

## PART 2: Enhanced Type Detection

### Type System Design
Detect and handle these column types:
- **`text`** - Default for non-numeric
- **`numeric`** - Plain numbers: 123, 45.67
- **`currency`** - Contains $€£¥: "$1,234.56"
- **`percentage`** - Contains %: "3.5%", "12%"
- **`date`** - Parseable dates: "2024-01-15", "Jan 15 2024"

### Backend Changes

**Fix `clean_numeric_value()` in generic_processor.py:**
```python
@staticmethod
def clean_numeric_value(value: str) -> float:
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    value_str = str(value).strip()

    # Detect if it's a percentage
    is_percentage = '%' in value_str

    # Remove currency and formatting
    value_str = re.sub(r'[$€£¥₹]', '', value_str)
    value_str = value_str.replace(',', '')
    value_str = value_str.replace('%', '')
    value_str = value_str.strip()

    try:
        result = float(value_str)
        # Convert percentage to decimal (3% -> 0.03)
        if is_percentage:
            result = result / 100.0
        return result
    except (ValueError, AttributeError):
        return 0.0
```

**Add new function `detect_column_type()` in generic_processor.py:**
```python
def detect_column_type(series: pd.Series) -> dict:
    """
    Returns: {
        'type': 'numeric'|'currency'|'percentage'|'date'|'text',
        'confidence': 0.0-1.0,
        'sample_values': [...],
        'suggested_display_name': str
    }
    """
    # Sample first 1000 non-null values
    sample = series.dropna().head(1000)

    if len(sample) == 0:
        return {'type': 'text', 'confidence': 0.0}

    # Check for percentage (look for % symbol)
    pct_count = sum('%' in str(val) for val in sample)
    if pct_count / len(sample) > 0.8:
        return {'type': 'percentage', 'confidence': pct_count/len(sample)}

    # Check for currency
    currency_pattern = r'[$€£¥₹]'
    curr_count = sum(bool(re.search(currency_pattern, str(val))) for val in sample)
    if curr_count / len(sample) > 0.8:
        return {'type': 'currency', 'confidence': curr_count/len(sample)}

    # Check for date
    try:
        parsed = pd.to_datetime(sample, errors='coerce')
        date_ratio = parsed.notna().sum() / len(sample)
        if date_ratio > 0.8:
            return {'type': 'date', 'confidence': date_ratio}
    except:
        pass

    # Check if numeric
    cleaned = sample.apply(GenericProcessor.clean_numeric_value)
    numeric_ratio = (cleaned != 0).sum() / len(sample)
    if numeric_ratio > 0.8:
        return {'type': 'numeric', 'confidence': numeric_ratio}

    return {'type': 'text', 'confidence': 1.0}
```

**Enhance `analyze_columns()` in generic_processor.py:**
- Call `detect_column_type()` for each column
- Return enhanced metadata:
  ```python
  {
      'name': 'ad_spend',
      'type': 'currency',
      'confidence': 0.95,
      'sample': '$1,234.56',
      'unique_count': 150,
      'suitable_for_value': True,
      'suggested_display_name': 'Ad Spend'
  }
  ```

**Add `prettify_column_name()` utility:**
```python
def prettify_column_name(name: str) -> str:
    """Convert snake_case or camelCase to Title Case"""
    # Handle snake_case: num_widgets -> Num Widgets
    result = name.replace('_', ' ')
    # Handle camelCase: numWidgets -> num Widgets
    result = re.sub(r'([A-Z])', r' \1', result)
    # Title case each word
    result = result.strip().title()
    return result
```

### Frontend Changes

**ColumnSelector.vue:**
- Display type icon next to column name:
  - 💵 currency
  - % percentage
  - 📅 date
  - 📊 numeric
  - 📝 text
- Show confidence: "Detected as Currency (95% confidence)"
- Add inline type override dropdown (optional, collapsed by default)
- If confidence < 90%, show warning icon and suggest user verify

**FileLoaderModal.vue Step 3 (Value Column):**
- Only show numeric, currency, and percentage columns
- For percentage columns, add toggle: "Store as decimal (0.03) or keep as-is (3.0)"
- Display detected type prominently

---

## PART 3: Display Names

### UX Flow
In **Step 2 (Configure Hierarchy)** after selecting columns:
- Show expandable section: "✏️ Customize Display Names (Optional)"
- When expanded, show table:
  ```
  Column Name          Display Name
  -------------        -----------------
  num_widgets    →    [Number of Widgets]  (editable input)
  dsp_name       →    [DSP Name]           (editable input)
  ```
- Pre-fill with smart defaults using `prettify_column_name()`
- User can edit inline
- Same for value column in Step 3

### Backend Changes

**Modify metadata structure:**
```python
{
    'chart_name': 'My Chart',
    'tree_order': ['dsp_name', 'brand_name'],
    'value_column': 'ad_spend',
    'display_names': {
        'dsp_name': 'DSP Platform',
        'brand_name': 'Brand Name',
        'ad_spend': 'Ad Spend ($)'
    },
    'column_types': {
        'ad_spend': 'currency',
        'rate': 'percentage'
    },
    'header_row': 0,
    'skip_rows': 0,
    'source_file': '...',
    'data': {...}
}
```

**Modify `build_tree_recursive()`:**
- Use display names for node labels instead of column names
- Keep original names in metadata for filtering

**Modify `/api/process`:**
- Accept `displayNames` object in request body
- Pass to `GenericProcessor`
- Store in metadata JSON

### Frontend Changes

**FileLoaderModal.vue:**
- Add state: `displayNames = ref({})`
- Add state: `showDisplayNames = ref(false)` (toggle)
- After hierarchy selection, show "Customize Display Names" section
- For each column in `hierarchyColumns` and `valueColumn`:
  - Original name (read-only, gray)
  - → arrow
  - Display name input (editable, pre-filled with prettified version)
- Pass `displayNames` to `/api/process`

**App.vue:**
- Receive display names from metadata
- Store in `displayNames = ref({})`
- Create computed property:
  ```js
  const getDisplayName = (colName) => {
    return displayNames.value[colName] || colName
  }
  ```
- Pass to child components

**SunburstChart.vue:**
- Accept `displayNames` prop
- Use display names for chart labels

**PageHeader.vue (Breadcrumbs):**
- Accept `displayNames` prop
- Use display names in breadcrumb path

**DataTable.vue:**
- Modify `prettyHeader()` to use display names
- Map display names to original names for filtering

**DataPane.vue:**
- Use display names for labels

---

## Backwards Compatibility

**Handle old sessions without new fields:**
```python
header_row = metadata.get('header_row', 0)
skip_rows = metadata.get('skip_rows', 0)
display_names = metadata.get('display_names', {})
column_types = metadata.get('column_types', {})
```

**Fallback behavior:**
- No header_row: Use 0 (current behavior)
- No display_names: Use original column names
- No column_types: Use basic type detection

---

## Key Knock-On Effects

1. **CSV Export**: Use display names in exported headers
2. **Filtering**: Map display names → original names internally
3. **Error Messages**: Use display names for clarity
4. **Chart Labels**: All use display names
5. **Progress Messages**: "Processing DSP Platform..." (display name)
6. **Validation**: Ensure display names don't break JSON/API
7. **Mobile UI**: Display name inputs need responsive design
8. **Session Metadata**: Grows larger - ensure no storage limits

---

## Implementation Order

1. **Phase 1: Header Row Detection** (Least risky, high value)
   - Backend: `/api/file-preview` endpoint
   - Backend: Modify `file-info` and `process` to accept header params
   - Frontend: Add Step 1.5 with raw preview table
   - Test with various CSV formats

2. **Phase 2: Enhanced Type Detection** (Medium complexity)
   - Backend: Implement `detect_column_type()` and fix percentage handling
   - Backend: Update `analyze_columns()` to return type info
   - Frontend: Display type icons and confidence
   - Test with currency, percentage, date columns

3. **Phase 3: Display Names** (Most changes across codebase)
   - Backend: Modify metadata structure and tree building
   - Frontend: Add display name inputs to modal
   - Frontend: Update all components to use display names
   - Add `prettify_column_name()` utility
   - Test throughout entire flow

---

## Testing Strategy

- **Header Row**: Test CSVs with 0, 1, 2, 3+ title rows
- **Types**: Test files with mixed percentages (3%, 0.03), currencies ($, €, £), dates
- **Display Names**: Test with long names, special characters, duplicates
- **Edge Cases**: Empty columns, all-null columns, very large files
- **Backwards Compat**: Load old session JSONs, ensure they still work
- **Mobile**: Test all new UI on small screens

---

## Estimated Component Changes

**Backend** (4 files):
- `routes.py`: +40 lines (new endpoint, param handling)
- `generic_processor.py`: +120 lines (type detection, display names, header handling)

**Frontend** (5 files):
- `FileLoaderModal.vue`: +150 lines (new step, display names UI)
- `ColumnSelector.vue`: +80 lines (type icons, display name inputs)
- `App.vue`: +30 lines (display name mapping)
- `SunburstChart.vue`: +20 lines (use display names)
- `DataTable.vue`: +25 lines (display name headers)
- `PageHeader.vue`: +15 lines (display name breadcrumbs)
- `DataPane.vue`: +10 lines (display names)

**Total**: ~490 lines of new/modified code
