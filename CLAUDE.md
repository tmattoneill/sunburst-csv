# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sunburst CSV is a full-stack web application that converts hierarchical CSV/XLSX data into interactive sunburst visualizations. Users upload data, select columns for hierarchy, choose a value metric, and generate navigable charts with drill-down capabilities.

## Development Commands

### Local Development (Recommended)
```bash
# Start both backend and frontend with auto-reload
./runapp.sh

# Stop all services
./stopapp.sh
```

**Access URLs:**
- Frontend: http://localhost:8080
- Backend: http://localhost:6500/api/health

The `runapp.sh` script:
- Creates Python virtual environment if needed
- Installs/updates dependencies automatically
- Runs Flask backend with Gunicorn (port 6500)
- Runs Vue frontend dev server (port 8080)
- Logs to `backend.log` and `frontend.log`

### Docker Development
```bash
# Build and start containers
docker compose up --build

# Access at http://localhost:3000
```

### Backend Only
```bash
cd backend/app
source ../venv/bin/activate
pip install -r ../requirements.txt
python main.py  # Runs on port 6500
```

### Frontend Only
```bash
cd frontend
npm install
npm run serve  # Runs on port 8080
npm run build  # Production build
npm run lint   # Lint code
```

## Architecture

### Session Isolation
- Each user gets a unique session ID stored in localStorage
- Backend stores session-specific data files: `{session_id}_sunburst_data.json`
- Prevents data conflicts between concurrent users
- Session persists across page reloads but clears with localStorage/incognito mode

### Data Flow

1. **Upload & Analysis** (`FileLoaderModal.vue`)
   - POST `/api/upload` → saves to `backend/data/raw/`
   - GET `/api/file-info` → analyzes columns using `analyze_columns()`
   - User configures hierarchy (3+ levels) and value column
   - POST `/api/validate-columns` → validates selection

2. **Processing** (`GenericProcessor`)
   - POST `/api/process` → streams progress via Server-Sent Events
   - Reads CSV/XLSX, cleans numeric values (handles currency, commas, %)
   - Builds recursive tree structure by grouping and summing
   - Saves to `{session_id}_sunburst_data.json`

3. **Visualization** (`SunburstChart.vue`)
   - GET `/api/data?session_id=X` → loads chart data
   - ECharts renders sunburst with click/hover interactions
   - Breadcrumb navigation via `PageHeader.vue`
   - Color palettes: Ocean, Sunset, Forest, Monochrome

4. **Table Display** (`DataTable.vue`)
   - GET `/api/table-data` → reads original CSV with filters
   - Filters based on current chart path
   - Pagination (20 rows/page)
   - CSV export of filtered data

### Key Processing Logic

**GenericProcessor** (`backend/app/dataproc/generic_processor.py`):
- `read_dataframe()`: Loads CSV/XLSX with pandas
- `validate_and_prepare_data()`: Validates columns, cleans values, removes NaN
- `build_tree_recursive()`: Recursively groups by hierarchy levels, sums values
- `create_sunburst_data()`: Orchestrates pipeline with progress callbacks

**Progress Tracking**:
- Uses Python `queue.Queue()` and threading for SSE
- Progress percentages: 0-10% reading, 10-20% validation, 20-90% tree building, 90-100% finalization
- Frontend displays live status in modal overlay

### Frontend State Management

**App.vue** is the orchestrator:
- `chartData`: Full tree structure from backend
- `currentPath`: Array of nodes from root to current view
- `currentFilters`: Object mapping hierarchy columns to selected values
- `selectedNode`: User-clicked node (sticky)
- `hoveredNode`: Mouse-over node (temporary preview)
- `dataPaneNode`: Computed as `hoveredNode || selectedNode` for data display

**Navigation Flow**:
1. User clicks segment → `handleNodeClick()` updates `selectedNode`
2. Chart emits `path-change` → `handlePathChange()` rebuilds filters
3. Filters propagate to `DataTable` → re-queries CSV with filters
4. Breadcrumb click → `handlePathNavigation()` walks tree to target node

## Important Code Patterns

### Numeric Value Cleaning
The `clean_numeric_value()` method handles diverse formats:
```python
# "$54,500.02" → 54500.02
# "1,234.56" → 1234.56
# "2.5%" → 2.5
```
Used for both value column and column type detection.

### API Base URL Configuration
Frontend dynamically determines API URL via `window.location.origin`:
```javascript
// frontend/src/services/api.js
const API_BASE_URL = `${window.location.origin}/api`
```
This allows the app to work across different deployment environments without hardcoded URLs.

### Session ID Passing
Always include `session_id` in API requests:
```javascript
await fetchApi(API_ENDPOINTS.DATA, {
  params: { session_id: sessionId.value }
})
```

### Legacy Mode Support
The app supports older "security report" format (using SQLite) alongside generic CSV mode. Detection happens by checking for `chart_name` in metadata JSON. **Most new work should focus on generic mode.**

## Common Tasks

### Add a New Color Palette
1. Define palette in `SunburstChart.vue` `colorPalettes` object
2. Add to dropdown in `PageHeader.vue` palette selector
3. No backend changes needed

### Add a New Column Type Detector
Edit `analyze_columns()` in `generic_processor.py` to add type detection logic.

### Change Progress Messages
Modify `_report_progress()` calls in `GenericProcessor.create_sunburst_data()` and `build_tree_recursive()`.

### Adjust Data Validation Rules
Edit `validate_column_selection()` in `generic_processor.py` for stricter/looser validation.

## File Locations

**Backend:**
- `backend/app/api/routes.py`: All API endpoints
- `backend/app/dataproc/generic_processor.py`: CSV processing pipeline
- `backend/app/dataproc/report_processor.py`: Legacy security reports (rarely used)
- `backend/data/raw/`: Uploaded files
- `backend/data/*.json`: Session-specific chart data

**Frontend:**
- `frontend/src/App.vue`: Main orchestrator, state management
- `frontend/src/components/SunburstChart.vue`: ECharts visualization
- `frontend/src/components/FileLoaderModal.vue`: 4-step upload wizard
- `frontend/src/components/DataTable.vue`: Tabular data with filters
- `frontend/src/services/api.js`: API client with fetch wrapper

## Troubleshooting

### Backend Not Starting
- Check if port 6500 is already in use: `lsof -i :6500`
- Look for errors in `backend.log`
- Verify virtual environment is activated

### Frontend Build Errors
- Delete `node_modules` and `package-lock.json`, then `npm install`
- Check for missing Bootstrap/ECharts in dependencies

### Data Not Loading
- Check browser localStorage for `sunburst_session_id`
- Verify `backend/data/{session_id}_sunburst_data.json` exists
- Check Network tab for API errors (401, 404, 500)

### Progress Bar Stuck
- Check backend console for Python exceptions
- SSE connection might be interrupted—look for CORS errors
- Ensure `progress_callback` is being called in `GenericProcessor`

## Tech Stack Notes

- **Flask** application factory pattern in `api/__init__.py`
- **Gunicorn** for production serving (configured in `runapp.sh`)
- **Vue 3 Composition API** with `<script setup>` syntax
- **ECharts** sunburst type with custom roam/click handlers
- **Bootstrap 5** for UI (modals, buttons, forms)
- **Pandas** for all CSV/Excel operations
- **Server-Sent Events** for unidirectional streaming (process endpoint)
