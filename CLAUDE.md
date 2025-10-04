# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sunchart is a security data visualization tool that processes CSV/Excel security incident reports and displays them as interactive sunburst charts. It uses a Flask backend for data processing and a Vue 3 frontend for visualization.

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
- `backend/app/api/routes.py` - REST API endpoints
- `backend/app/dataproc/report_processor.py` - CSV/Excel processing, hierarchical tree building
- `backend/app/dataproc/db_handler.py` - SQLite operations
- `backend/app/dataproc/security_data_handler.py` - Report type detection (basic/enhanced/detailed/full)

### Frontend Structure
- **Port:** 3000 (Docker) or 8080 (npm run serve)
- **Framework:** Vue 3 with Composition API
- **Visualization:** ECharts for sunburst charts
- **HTTP Client:** Axios

**Key Components:**
- `frontend/src/App.vue` - Main app container, manages state between chart and table
- `frontend/src/components/SunburstChart.vue` - Interactive sunburst visualization
- `frontend/src/components/DataTable.vue` - Paginated data table with filtering
- `frontend/src/components/DataPane.vue` - Shows details of selected/hovered nodes
- `frontend/src/components/FileLoaderModal.vue` - File upload interface
- `frontend/src/components/PageHeader.vue` - Report metadata display
- `frontend/src/components/PathBar.vue` - Breadcrumb navigation
- `frontend/src/services/api.js` - API client with endpoints

## Data Flow & Processing

### Upload → Process → Visualize Pipeline

1. **File Upload** (`POST /api/upload`)
   - Accepts CSV, XLS, XLSX files
   - Excel files auto-converted to CSV using `openpyxl`
   - Saved to `backend/data/raw/`

2. **Report Processing** (`POST /api/process`)
   - `ReportProcessor` parses file and extracts:
     - First 4 rows: metadata (report type, date range)
     - Row 4: Column headers
     - Remaining rows: data
   - Data loaded into SQLite via `DatabaseHandler.initialize_db_from_dataframe()`
   - `SecurityDataHandler.detect_report_type()` determines report type based on available columns

3. **Tree Building** (`ReportProcessor.build_tree()`)
   - Creates hierarchical structure using `tree_order` columns
   - **Important:** Uses `.groupby()` with unique tag counts, not raw row counts
   - Each node's value = count of unique `tag_name` values at that level
   - Saves to `backend/data/sunburst_data.json`

4. **Visualization** (`GET /api/data`)
   - Frontend fetches JSON and renders sunburst chart
   - User clicks nodes to drill down
   - Path tracked via `PathBar` component
   - Filters applied to DataTable based on current path

5. **Table Data** (`GET/POST /api/table-data`)
   - Backend queries SQLite with filters from selected path
   - Returns paginated results (default: 20 items/page)
   - POST endpoint exports filtered data as CSV

### Report Type Detection

The `SecurityDataHandler` normalizes column names and detects 4 report types:

- **Basic:** incident, tag_name, hit_type (minimum required columns)
- **Enhanced:** + threat_behavior, malware_condition
- **Detailed:** + publisher_name, country, named_threat
- **Full:** + report_period_hit_count, tag_status

The `tree_order` (hierarchy) adjusts based on detected type.

## Expected File Format

CSV/Excel files must have:

**Rows 1-4 (metadata):**
1. Report type name
2. Date range: `"MM/DD/YYYY HH:MM - MM/DD/YYYY HH:MM"`
3. Empty or additional metadata
4. Column headers

**Required columns:** incident, tag_name, hit_type

**Common optional columns:** threat_behavior, publisher_name, country, malware_condition, named_threat, scan_date, etc.

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/data` - Get visualization data (sunburst tree + metadata)
- `POST /api/upload` - Upload CSV/XLS/XLSX file
- `POST /api/process` - Process uploaded file (params: clientName, filePath)
- `GET /api/table-data` - Get paginated table data with filters
- `POST /api/table-data` - Export filtered data as CSV

## State Management (Frontend)

App.vue manages shared state:
- `chartData` - Full sunburst tree structure
- `selectedNode` - Last clicked node (sticky)
- `hoveredNode` - Currently hovered node (temporary)
- `currentPath` - Breadcrumb path for navigation
- `currentFilters` - Filters sent to DataTable
- `filterOrder` - Tree hierarchy order

**DataPane Display Logic:**
- Shows `hoveredNode` if hovering, otherwise shows `selectedNode`
- Clicking a node makes it "stick" until another node is clicked
- Hovering temporarily overrides the display

## Important Implementation Details

### Tree Building Algorithm
The tree-building in `report_processor.py` uses **unique tag counts**, not raw row counts:
```python
# Groups by path, counts unique tag_names
counts = df.groupby(levels)['tag_name'].nunique()
```
This is critical for accurate visualization - do not change to `.count()`.

### Database Connection Pattern
All database operations use context managers for thread safety:
```python
with self.get_connection() as conn:
    # operations
    conn.commit()
```
Never share connection objects across requests.

### Column Normalization
All column names are normalized via:
```python
field.lower().strip().replace(' ', '_')
```
This ensures "Tag Name" → "tag_name" consistently.

### Path-Based Filtering
When user clicks a chart node, the path is built from root to node:
```python
path = ['All Data', 'hit_type:Alert', 'threat_behavior:Malware']
```
This is converted to SQL filters in `db_handler.get_table_data()`.

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

## Known Issues & Limitations

1. **Single-user application** - No authentication, shared database
2. **No file validation** - Uploads not scanned for malicious content
3. **Memory constraints** - Large files (>100MB) may cause issues
4. **Hardcoded date format** - Expects `%m/%d/%Y %H:%M` format
5. **CORS wide open** - Allows all origins (development only)

## Testing Notes

The application has no automated tests. Manual testing checklist in DIAGNOSTICS.md includes:
- Upload CSV/Excel files
- Verify chart rendering
- Click/hover interactions
- Table filtering and pagination
- CSV export functionality

## Docker Configuration

Services defined in `docker-compose.yml`:
- **backend:** Builds from `backend/Dockerfile`, volume mounts `backend/data` for persistence
- **frontend:** Builds from `frontend/Dockerfile`, uses Nginx to serve static files

Backend Dockerfile sets `WORKDIR /app/app` - this is critical as `main.py` expects to be run from the `app/` directory.
