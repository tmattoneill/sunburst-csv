# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sunchart is a **generic hierarchical data visualization tool** that creates interactive sunburst charts from any CSV/Excel file with hierarchical data. It uses a Flask backend for data processing and a Vue 3 frontend for visualization.

**Key Feature:** User-driven configuration - no hardcoded column assumptions. Works with any dataset containing nested categories and numeric values.

## Common Commands

### Docker (Recommended)
```bash
# Start application
docker-compose up --build

# Stop application
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v

# View backend logs
docker logs sunchart-backend-1
```

### Development (Local)

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd app
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run serve    # Development server
npm run build    # Production build
npm run lint     # Lint code
```

## Architecture

### Backend Structure
- **Port:** 6500
- **Framework:** Flask + Flask-CORS + Gunicorn
- **Database:** SQLite (`backend/data/security.db`)
- **Data Processing:** Pandas

**Key Modules:**
- `backend/app/api/routes.py` - REST API endpoints (supports dual mode)
- `backend/app/dataproc/generic_processor.py` - **NEW:** Generic hierarchical data processor
- `backend/app/dataproc/report_processor.py` - Legacy security report processor
- `backend/app/dataproc/db_handler.py` - SQLite operations
- `backend/app/dataproc/security_data_handler.py` - Legacy report type detection

### Frontend Structure
- **Port:** 3000 (Docker) or 8080 (npm run serve)
- **Framework:** Vue 3 with Composition API
- **Visualization:** ECharts for sunburst charts
- **HTTP Client:** Axios

**Key Components:**
- `frontend/src/App.vue` - Main app container, manages state (generic + legacy modes)
- `frontend/src/components/FileLoaderModal.vue` - **NEW:** 4-step upload wizard
- `frontend/src/components/ColumnSelector.vue` - **NEW:** Drag-and-drop hierarchy builder
- `frontend/src/components/SunburstChart.vue` - Interactive sunburst visualization
- `frontend/src/components/DataTable.vue` - Paginated data table with filtering
- `frontend/src/components/DataPane.vue` - Shows details of selected/hovered nodes
- `frontend/src/components/PageHeader.vue` - Chart metadata display (generic + legacy)
- `frontend/src/components/PathBar.vue` - Breadcrumb navigation
- `frontend/src/services/api.js` - API client with endpoints

## Generic Mode Workflow (Primary)

### User Experience Flow

1. **Upload File**
   - Click upload button
   - Select CSV/XLSX file (any structure)
   - File analyzed automatically

2. **Configure Hierarchy**
   - View available columns with data types
   - Select 3+ columns for hierarchy (drag to reorder)
   - Example: `dsp_name` → `brand_name` → `buyer_name`

3. **Select Value Column**
   - Choose numeric column to aggregate
   - Example: `ad_spend`, `impressions`, `revenue`

4. **Name & Create**
   - Name your visualization
   - Review configuration summary
   - Click "Create Visualization"

### Data Processing Pipeline

1. **File Upload** (`POST /api/upload`)
   - Accepts CSV, XLS, XLSX files
   - Excel files auto-converted to CSV
   - Saved to `backend/data/raw/`

2. **Column Analysis** (`GET /api/file-info?filePath=xxx`)
   - Reads file, detects column data types
   - Returns: `{columns: [{name, type, sample, suitable_for_value}], rowCount, preview}`
   - Identifies numeric columns for value selection

3. **Validation** (`POST /api/validate-columns`)
   - Request: `{filePath, treeOrder: [], valueColumn}`
   - Validates: min 3 hierarchy levels, value column is numeric
   - Returns: `{valid, errors[], warnings[]}`

4. **Processing** (`POST /api/process` - Generic Mode)
   - Request: `{filePath, chartName, treeOrder, valueColumn}`
   - `GenericProcessor` creates hierarchical tree:
     - Reads CSV/XLSX directly (no metadata row parsing)
     - Groups by hierarchy columns: `df.groupby(treeOrder)[valueColumn].sum()`
     - Builds recursive tree structure with aggregated values
     - Handles currency formatting (`$1,234.56` → `1234.56`)
   - Saves to `backend/data/sunburst_data.json`

5. **Visualization** (`GET /api/data`)
   - Returns: `{chart_name, tree_order, value_column, data: {name, value, children}}`
   - Frontend renders sunburst chart
   - User interacts: click to drill down, hover for details

## Legacy Mode (Security Reports)

Maintained for backward compatibility with security incident reports.

### Expected File Format

**Rows 1-4 (metadata):**
1. Report type name
2. Date range: `"MM/DD/YYYY HH:MM - MM/DD/YYYY HH:MM"`
3. Empty or additional metadata
4. Column headers

**Required columns:** incident, tag_name, hit_type

### Processing

- `POST /api/process` with `{clientName, filePath}` (no treeOrder/valueColumn)
- Routes to `ReportProcessor` (legacy)
- Auto-detects report type: basic/enhanced/detailed/full
- Uses unique `tag_name` counts for values

## API Endpoints

**Generic Mode:**
- `GET /api/file-info?filePath=xxx` - Analyze uploaded file columns
- `POST /api/validate-columns` - Validate user's column selection
- `POST /api/process` - Process file (generic: chartName, treeOrder, valueColumn)

**Legacy Mode:**
- `POST /api/process` - Process file (legacy: clientName, filePath only)

**Shared:**
- `GET /api/health` - Health check
- `GET /api/data` - Get visualization data (sunburst tree + metadata)
- `POST /api/upload` - Upload CSV/XLS/XLSX file
- `GET /api/table-data` - Get paginated table data with filters
- `POST /api/table-data` - Export filtered data as CSV

## Important Implementation Details

### Generic Tree Building Algorithm

**Location:** `backend/app/dataproc/generic_processor.py`

```python
def build_tree_recursive(df, tree_order, value_column, level=0):
    if level >= len(tree_order):
        return []

    col = tree_order[level]
    children = []

    for value in df[col].unique():
        subset = df[df[col] == value]
        node_value = subset[value_column].sum()  # Sum, not count
        child_nodes = build_tree_recursive(subset, tree_order, value_column, level + 1)

        children.append({
            'name': str(value),
            'value': float(node_value),
            'children': child_nodes
        })

    return sorted(children, key=lambda x: x['value'], reverse=True)
```

**Key Differences from Legacy:**
- Sums actual numeric values (not unique tag counts)
- Works with any column names (not hardcoded)
- No metadata row parsing required

### Currency & Number Cleaning

**Location:** `GenericProcessor.clean_numeric_value()`

Handles formats:
- `"$54,500.02"` → `54500.02`
- `"1,234.56"` → `1234.56`
- `"2.5%"` → `2.5`

### Column Type Detection

**Location:** `generic_processor.analyze_columns()`

Returns for each column:
```python
{
    'name': 'ad_spend',
    'type': 'numeric',  # or 'text'
    'sample': '$54,500.02',
    'unique_count': 847,
    'suitable_for_value': True  # Only if numeric
}
```

### Frontend Multi-Step Wizard

**Location:** `frontend/src/components/FileLoaderModal.vue`

4 steps with validation at each stage:
1. File upload
2. Hierarchy column selection (ColumnSelector component)
3. Value column selection
4. Chart naming and review

Progress stepper shows current step, validation prevents proceeding if invalid.

### Database Connection Pattern

All database operations use context managers for thread safety:
```python
with self.get_connection() as conn:
    # operations
    conn.commit()
```
Never share connection objects across requests.

### Path-Based Filtering

When user clicks a chart node, the path is built from root to node:
```python
path = ['All Data', 'dsp_name:The Trade Desk', 'brand_name:Johnson & Johnson']
```
This is converted to SQL filters in `db_handler.get_table_data()`.

## Example: RTB Data

File: `data/raw/rtb_data.csv`

**Configuration:**
- Hierarchy: `dsp_name` → `brand_name` → `buyer_name`
- Value Column: `ad_spend` (formatted as `" $54,500.02 "`)
- Chart Name: "RTB Ad Spend by DSP and Brand"

**Result:**
- Top level: DSPs (The Trade Desk, DV360, Amazon, etc.)
- Second level: Brands per DSP
- Third level: Buyers per brand
- Values: Total ad spend aggregated at each level

## State Management (Frontend)

`App.vue` manages shared state:
- `chartData` - Full sunburst tree structure
- `chartName` - User-provided or data name
- `treeOrder` - Hierarchy column names
- `reportType` - Legacy mode only (empty in generic mode)
- `dateStart`, `dateEnd` - Legacy mode only (empty in generic mode)
- `selectedNode` - Last clicked node (sticky)
- `hoveredNode` - Currently hovered node (temporary)
- `currentPath` - Breadcrumb path for navigation
- `currentFilters` - Filters sent to DataTable

**Dual Mode Detection:**
Frontend checks for `chart_name` in API response:
- If present → Generic mode
- If absent → Legacy mode (uses `report_type`, dates)

## Environment Variables

**Backend:**
- `DATA_DIR` - Data directory (default: `../data`)
- `UPLOAD_DIR` - Upload directory (default: `../data/raw`)
- `DATABASE_URL` - SQLite path (default: `../data/security.db`)
- `FLASK_ENV` - Flask environment (production/development)
- `HOST` - Server host (default: 0.0.0.0)
- `FLASK_PORT` - Server port (default: 6500)

**Frontend:**
- `VUE_APP_API_BASE_URL` - Backend API URL (set in `frontend/.env`)

## Validation Rules

**Frontend:**
- File must be CSV/XLSX
- Min 3 hierarchy columns
- Exactly 1 value column
- Value column must be numeric
- Chart name required (non-empty)
- Hierarchy columns cannot include value column

**Backend:**
- Selected columns must exist in file
- Value column must contain mostly numeric data (>50% valid)
- Hierarchy columns must have sufficient variety (min 2 unique values each)
- Min 10 data rows required

## Known Issues & Limitations

1. **Single-user application** - No authentication, shared database
2. **No file validation** - Uploads not scanned for malicious content
3. **Memory constraints** - Large files (>100MB) may cause issues
4. **CORS wide open** - Allows all origins (development only)
5. **No undo** - Cannot revert to previous visualization without re-upload

## Testing Notes

The application has no automated tests. Manual testing workflow:

**Generic Mode:**
1. Upload `data/raw/rtb_data.csv`
2. Select hierarchy: `dsp_name` → `brand_name` → `buyer_name`
3. Select value: `ad_spend`
4. Name chart: "RTB Ad Spend Test"
5. Verify sunburst renders with correct values
6. Click nodes to drill down
7. Check DataTable filters correctly

**Legacy Mode:**
1. Upload security report CSV (4-row header format)
2. Enter client name
3. Verify auto-processing with report type detection

## Docker Configuration

Services defined in `docker-compose.yml`:
- **backend:** Builds from `backend/Dockerfile`, volume mounts `backend/data` for persistence
- **frontend:** Builds from `frontend/Dockerfile`, uses Nginx to serve static files

Backend Dockerfile sets `WORKDIR /app/app` - this is critical as `main.py` expects to be run from the `app/` directory.

## Migration Notes

**From Security-Specific to Generic:**

Old approach:
- Hardcoded columns (`tag_name`, `incident`, etc.)
- Automatic report type detection
- Unique tag counting

New approach:
- User selects any columns
- User defines hierarchy order
- Numeric value aggregation (sum)

**Backward Compatibility:**
- `/api/process` endpoint supports both modes
- Legacy `ReportProcessor` still functional
- Frontend detects mode from API response format
