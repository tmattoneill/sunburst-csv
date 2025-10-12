# Sunburst CSV

Interactive hierarchical data visualization tool for CSV and Excel files. Transform any tabular data with 3 or more nested categories into beautiful, explorable sunburst charts.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.5-green.svg)

## Overview

Sunburst CSV is a full-stack web application that converts hierarchical CSV/XLSX data into interactive sunburst visualizations. Users upload their data, select columns for the hierarchy, choose a value metric, and instantly generate navigable charts with drill-down capabilities and detailed data tables.

Originally built for security report analysis, this tool has been generalized to handle any hierarchical dataset, making it useful for:
- 📊 Budget and financial analysis
- 🛒 Sales and revenue breakdowns
- 🌐 Website analytics hierarchies
- 📱 Ad campaign performance tracking
- 🏢 Organizational structures
- 📈 Any data with nested categories

## Quick Start

### Prerequisites
- **Docker & Docker Compose**: For containerized deployment
- **OR Local Development**: Python 3.11+ and Node.js 20+

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/tmattoneill/sunburst-csv.git
cd sunburst-csv

# Start services
docker compose up --build
```

**Access at: http://localhost:3000**

To stop:
```bash
docker compose down
```

### Option 2: Local Development (Faster Iteration)

```bash
# Make scripts executable (first time only)
chmod +x runapp.sh stopapp.sh

# Start both backend and frontend
./runapp.sh
```

**Access at: http://localhost:8080**

The script automatically:
- Creates Python virtual environment
- Installs all dependencies
- Sets up data directories
- Starts backend (Flask + Gunicorn)
- Starts frontend (Vue dev server)

To stop:
```bash
./stopapp.sh
```

### Port Configuration

| Service | Docker | Local Dev | Notes |
|---------|--------|-----------|-------|
| Frontend | 3000 | 8080 | Vue dev server with hot reload |
| Backend API | 6500 | 6500 | Flask with Gunicorn |

Ports can be customized via `.env.dev` file. See configuration section below.

## Key Features

### 📤 Data Processing
- Upload CSV or XLSX files (any size)
- Automatic column type detection (numeric vs text)
- Smart value parsing: currency symbols ($), commas (1,234), percentages (25%)
- Graceful handling of missing data and NaN values
- Real-time preview of first 5 rows during upload
- Automatic header row detection

### 📊 Interactive Visualization
- Beautiful sunburst chart with smooth animations
- **Click** segments to drill down through hierarchy
- **Hover** to preview values without committing navigation
- Breadcrumb navigation for quick level jumping
- Multiple color palettes:
  - 🌊 Ocean (blues and teals)
  - 🌅 Sunset (warm oranges and reds)
  - 🌲 Forest (greens and earth tones)
  - ⚫ Monochrome (grayscale)
- Fully responsive design (desktop & tablet)
- Persistent zoom and pan controls

### 📋 Data Table View
- Dynamic columns generated from your data
- Intelligent column ordering (hierarchy → value → other fields)
- Real-time filtering based on chart selection
- Pagination (20 rows per page)
- CSV export of filtered results
- Automatic formatting of column headers (snake_case → Title Case)
- Sortable columns

### 🎯 Guided Workflow
Four-step upload wizard:
1. **Upload File** - Drop CSV or Excel file
2. **Configure Hierarchy** - Select and order 3+ columns (drag to reorder)
3. **Select Value Column** - Choose numeric field to aggregate
4. **Name and Create** - Real-time progress tracking with Server-Sent Events

Additional features:
- Auto-modal on first visit (no existing data)
- Column validation before processing
- Live progress bar with status messages
- Support for both generic CSV and legacy security report formats

### 🔒 Session Management
- Isolated user sessions via browser localStorage
- Unique session IDs prevent data conflicts
- Session persists across page reloads
- Clear localStorage or use incognito mode to reset

## Sample Datasets

The repository includes example datasets in `data_samples/`:

| File | Size | Use Case | Hierarchy Example |
|------|------|----------|-------------------|
| `ad_campaign_dataset.csv` | 32KB | Marketing spend analysis | Platform → Campaign → Ad Group |
| `global_sales_dataset.csv` | 42KB | Sales performance | Region → Country → Product |
| `website_analytics_dataset.csv` | 34KB | Traffic breakdown | Source → Medium → Page |
| `zmat_test_100.csv` | 1.1MB | Large dataset testing | Multi-level test data |

## Usage Guide

### Basic Workflow

1. **Upload Your Data**
   - On first load, the modal appears automatically
   - Or click "Upload Data" button anytime
   - Supported formats: `.csv`, `.xlsx`, `.xls`
   - Minimum requirements:
     - At least 3 columns for hierarchy
     - At least 1 numeric column for values

2. **Configure Hierarchy**
   - Select 3 or more columns in hierarchical order
   - **Drag and drop** to reorder
   - Example: `Region` → `Department` → `Team`
   - **Tip**: Start broad, end specific

3. **Choose Value Column**
   - Select the numeric field to aggregate
   - Common choices: revenue, count, amount, hours, budget
   - The tool automatically sums values for parent nodes

4. **Name Your Visualization**
   - Give it a descriptive name
   - Click "Create" to start processing
   - Watch live progress:
     - Reading file...
     - Validating data...
     - Building tree structure...
     - Finalizing...

5. **Explore Your Chart**
   - **Click** any segment to drill down
   - **Hover** to preview without navigating
   - **Breadcrumbs** show current path
   - **Color palette** selector in header
   - **Data table** below updates with current selection

6. **Analyze Filtered Data**
   - Table shows rows matching current selection
   - Use pagination to browse
   - Export filtered data as CSV
   - Click "Reset" to view all data

### Example Use Cases

**Marketing Spend Analysis:**
```
Hierarchy: platform → campaign_name → ad_group
Value: ad_spend
Result: See which platforms and campaigns consume most budget
```

**Sales Dashboard:**
```
Hierarchy: region → product_category → product_name
Value: revenue
Result: Identify top-performing regions and products
```

**Budget Tracking:**
```
Hierarchy: department → project → expense_category
Value: amount
Result: Visualize organizational spending patterns
```

## Technology Stack

### Backend
- **Python 3.11**
- **Flask 3.0** - Web framework
- **Pandas 2.2** - Data processing and CSV/Excel parsing
- **Gunicorn 23.0** - Production WSGI server
- **Flask-CORS 4.0** - Cross-origin resource sharing
- **openpyxl 3.1** - Excel file support
- **SQLite** - Legacy security report mode

### Frontend
- **Vue 3.5** - Composition API with `<script setup>`
- **ECharts 5.6** - Sunburst chart visualization
- **Axios 1.7** - HTTP client with interceptors
- **Bootstrap 5** (via CDN) - UI components
- **Vue CLI 5.0** - Build tooling

### DevOps
- **Docker** - Multi-stage builds for backend and frontend
- **Docker Compose** - Service orchestration
- **Nginx** (Alpine) - Frontend static file serving in production
- **Hot Reload** - Development mode for both backend and frontend

## Project Structure

```
sunburst-csv/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py           # Blueprint registration
│   │   │   └── routes.py             # All API endpoints (487 lines)
│   │   ├── dataproc/
│   │   │   ├── generic_processor.py  # CSV/XLSX processing (493 lines)
│   │   │   ├── report_processor.py   # Legacy security reports
│   │   │   ├── file_analyzer.py      # Column type detection
│   │   │   ├── type_detector.py      # Numeric value parsing
│   │   │   ├── db_handler.py         # SQLite operations
│   │   │   └── security_data_handler.py  # Legacy format handler
│   │   ├── __init__.py               # Flask app factory
│   │   └── main.py                   # Entry point
│   ├── data/
│   │   ├── raw/                      # Uploaded files
│   │   ├── processed/                # Intermediate data
│   │   └── {session_id}_sunburst_data.json  # Generated charts
│   ├── Dockerfile                    # Multi-stage Python build
│   └── requirements.txt              # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SunburstChart.vue     # ECharts visualization
│   │   │   ├── FileLoaderModal.vue   # 4-step upload wizard
│   │   │   ├── ColumnSelector.vue    # Drag-and-drop hierarchy builder
│   │   │   ├── DataTable.vue         # Paginated table with filters
│   │   │   ├── DataPane.vue          # Summary statistics
│   │   │   ├── PageHeader.vue        # Breadcrumb navigation
│   │   │   ├── PathBar.vue           # Path visualization
│   │   │   └── LandingPage.vue       # Initial welcome screen
│   │   ├── services/
│   │   │   └── api.js                # Axios client + endpoints
│   │   ├── utils/
│   │   │   └── errors.js             # Error handling
│   │   ├── config/
│   │   │   └── env.js                # Environment configuration
│   │   ├── App.vue                   # Root component (367 lines)
│   │   ├── main.js                   # Vue app initialization
│   │   └── palettes.js               # Color scheme definitions
│   ├── public/
│   │   └── index.html                # HTML entry point
│   ├── Dockerfile                    # Node build + Nginx serve
│   ├── package.json                  # Node dependencies
│   └── vue.config.js                 # Vue CLI configuration
├── data_samples/                     # Example CSV files
│   ├── ad_campaign_dataset.csv
│   ├── global_sales_dataset.csv
│   ├── website_analytics_dataset.csv
│   └── zmat_test_100.csv
├── docker-compose.yml                # Service orchestration
├── .env.dev                          # Port configuration
├── runapp.sh                         # Local dev startup script
├── stopapp.sh                        # Stop local services
├── run-docker.sh                     # Docker shortcut
├── stop-docker.sh                    # Docker stop shortcut
└── README.md                         # This file
```

## API Reference

All endpoints use `/api` prefix. Requests should include `session_id` parameter.

### Health Check
```http
GET /api/health

Response:
{
  "status": "healthy"
}
```

### Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

Form Data:
  file: <binary>
  session_id: <string> (optional)

Response:
{
  "filePath": "uploaded-file-20241012-083045.csv"
}
```

### Analyze File
```http
POST /api/analyze
Content-Type: application/json

Body:
{
  "filePath": "uploaded-file.csv",
  "session_id": "abc123"
}

Response:
{
  "columns": [
    {"name": "region", "type": "text", "sample": "North"},
    {"name": "revenue", "type": "numeric", "sample": 1500.50}
  ],
  "rowCount": 1234,
  "fileName": "uploaded-file.csv"
}
```

### Get File Info
```http
GET /api/file-info?filePath=<path>&session_id=<id>

Response:
{
  "columns": [...],
  "rowCount": 1234,
  "preview": [[...], [...], ...],  // First 5 rows
  "fileName": "uploaded-file.csv"
}
```

### Validate Columns
```http
POST /api/validate-columns
Content-Type: application/json

Body:
{
  "filePath": "uploaded-file.csv",
  "treeOrder": ["region", "department", "team"],
  "valueColumn": "revenue",
  "session_id": "abc123"
}

Response:
{
  "valid": true,
  "errors": []
}
```

### Process File (Server-Sent Events)
```http
POST /api/process
Content-Type: application/json

Body:
{
  "filePath": "uploaded-file.csv",
  "chartName": "Sales Analysis",
  "treeOrder": ["region", "department", "team"],
  "valueColumn": "revenue",
  "session_id": "abc123"
}

Response: (SSE stream)
data: {"status": "processing", "progress": 10, "message": "Reading file..."}
data: {"status": "processing", "progress": 50, "message": "Building tree..."}
data: {"status": "complete", "progress": 100, "message": "Done!"}
```

### Get Chart Data
```http
GET /api/data?session_id=<id>

Response:
{
  "chart_name": "Sales Analysis",
  "tree_order": ["region", "department", "team"],
  "value_column": "revenue",
  "source_file": "uploaded-file.csv",
  "data": {
    "name": "Sales Analysis",
    "value": 150000,
    "children": [...]
  }
}
```

### Get Table Data (Paginated)
```http
GET /api/table-data?page=1&items_per_page=20&session_id=<id>

Optional Query Params:
  filters: {"region": "North", "department": "Sales"}  // JSON string

Response:
{
  "data": [{...}, {...}, ...],
  "page": 1,
  "total": 1234,
  "total_pages": 62,
  "columns": ["region", "department", "team", "revenue"]
}
```

## Configuration

### Environment Variables

#### Root `.env.dev` (Docker & runapp.sh)
```bash
FRONTEND_PORT=8080  # Local dev Vue server
BACKEND_PORT=6500   # Flask API server
```

#### Frontend `.env.local` (Local development)
```bash
VUE_APP_BASE_URL=http://localhost:6500
```

Create this file in `frontend/.env.local` for local development. The Vue dev server needs to know where the backend API is located.

#### Frontend `.env.production` (Docker builds)
```bash
VUE_APP_BASE_URL=http://localhost:6500
```

For production deployments, update this to your actual domain.

### Docker Compose Configuration

```yaml
services:
  backend:
    ports:
      - "${BACKEND_PORT:-6500}:${BACKEND_PORT:-6500}"
    environment:
      - FLASK_PORT=${BACKEND_PORT:-6500}

  frontend:
    ports:
      - "${FRONTEND_PORT:-3000}:80"
```

The `:-` syntax provides default values if env vars aren't set.

## Development

### Backend Development

```bash
# Navigate to backend
cd backend/app

# Create and activate virtual environment
python3 -m venv ../venv
source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Run Flask in debug mode
python main.py
```

Backend will run on `http://localhost:6500` with auto-reload enabled.

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start dev server with hot reload
npm run serve

# Build for production
npm run build

# Lint and fix files
npm run lint
```

Frontend will run on `http://localhost:8080` with hot module replacement.

### Code Architecture

#### Backend: Generic Processor Pipeline
1. **Read CSV/XLSX** - Pandas reads file with automatic encoding detection
2. **Validate Columns** - Check existence and data types
3. **Clean Numeric Values** - Remove $ , % symbols, handle NaN
4. **Build Tree Recursively** - Group by hierarchy levels, sum values
5. **Generate Metadata** - Include tree_order, value_column, source_file
6. **Save to JSON** - Write `{session_id}_sunburst_data.json`

Key function: `create_sunburst_data()` in `generic_processor.py`

#### Frontend: State Management
1. **FileLoaderModal** - Handles upload and column selection
2. **App.vue** - Fetches chart data, manages navigation state
3. **SunburstChart** - Renders ECharts, emits click/hover events
4. **DataTable** - Queries filtered data based on current path
5. **All components** - React to path changes via props/events

Key state in `App.vue`:
- `chartData` - Full tree structure
- `currentPath` - Array of nodes from root to current view
- `currentFilters` - Object mapping hierarchy columns to values
- `selectedNode` - User-clicked node (sticky)
- `hoveredNode` - Mouse-over node (temporary preview)

## Data Formats

### Input CSV Structure

```csv
region,department,team,revenue,notes
North,Sales,Team A,15000,Q1 performance
North,Sales,Team B,22000,Top performers
North,Marketing,Team C,18000,Campaign spend
South,Sales,Team D,31000,Record quarter
```

**Requirements:**
- First row must be column headers
- At least 3 columns for hierarchy (more is fine)
- At least 1 numeric column for aggregation
- Values can include: `$1,234.56`, `50%`, `1234`, etc.

### Output JSON Structure

```json
{
  "chart_name": "Revenue by Region",
  "tree_order": ["region", "department", "team"],
  "value_column": "revenue",
  "source_file": "sales-data-20241012.csv",
  "data": {
    "name": "Revenue by Region",
    "value": 86000,
    "children": [
      {
        "name": "North",
        "value": 55000,
        "children": [
          {
            "name": "Sales",
            "value": 37000,
            "children": [
              {"name": "Team A", "value": 15000, "children": []},
              {"name": "Team B", "value": 22000, "children": []}
            ]
          },
          {
            "name": "Marketing",
            "value": 18000,
            "children": [
              {"name": "Team C", "value": 18000, "children": []}
            ]
          }
        ]
      },
      {
        "name": "South",
        "value": 31000,
        "children": [...]
      }
    ]
  }
}
```

## Troubleshooting

### Docker Issues

**Containers won't start:**
```bash
docker compose down
docker system prune -f
docker compose up --build
```

**Can't access frontend:**
- Verify at: http://localhost:3000
- Check containers: `docker ps`
- Check logs: `docker logs sunburst-csv-frontend-1`
- Check backend health: `curl http://localhost:6500/api/health`

**Port conflicts:**
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :6500

# Change ports in .env.dev
echo "FRONTEND_PORT=3001" >> .env.dev
echo "BACKEND_PORT=6501" >> .env.dev
```

### Local Development Issues

**Backend won't start:**
```bash
# Check logs
tail -f backend.log

# Verify Python version
python3 --version  # Should be 3.11+

# Check port availability
lsof -i :6500

# Manually test
cd backend/app
source ../venv/bin/activate
python main.py
```

**Frontend won't start:**
```bash
# Check logs
tail -f frontend.log

# Verify Node.js version
node --version  # Should be 20+

# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check port availability
lsof -i :8080
```

**Services still running:**
```bash
# Use stop script
./stopapp.sh

# Or manually kill processes
pkill -f gunicorn
pkill -f "npm run serve"
pkill -f "vue-cli-service"

# Verify nothing is running
ps aux | grep -E "(gunicorn|vue-cli-service|npm)"
```

### Upload Issues

**Upload fails with 400 error:**
- Verify file format (CSV, XLSX, XLS only)
- Check file size (recommend under 100MB)
- Ensure first row contains column headers
- Check for special characters in headers
- Look at backend logs: `tail -f backend.log`

**No columns appear in hierarchy selector:**
- Confirm upload succeeded (check Network tab in DevTools)
- Verify backend is running: `curl http://localhost:6500/api/health`
- Check console for API errors (F12 → Console)
- Ensure file has at least 3 columns

**Column validation fails:**
- Need minimum 3 hierarchy columns
- Value column must be numeric
- Check for all-NaN value column
- Verify column names don't have special characters

### Visualization Issues

**Chart not rendering:**
```bash
# Check browser console for errors
# F12 → Console tab

# Verify data exists
curl http://localhost:6500/api/data?session_id=YOUR_SESSION_ID

# Check ECharts initialization
# Console should show: "Chart initialized successfully"

# Hard refresh browser
# Chrome/Edge: Ctrl+Shift+R
# Mac: Cmd+Shift+R
```

**Chart shows but no interactions work:**
- Check for JavaScript errors in console
- Verify ECharts version (should be 5.6.0)
- Try different browser
- Clear browser cache

**Colors look wrong:**
- Try different color palette in header dropdown
- Check browser color settings
- Verify ECharts theme is loading

### Data Table Issues

**Table shows no rows:**
- Ensure file was processed successfully
- Check source CSV still exists in `backend/data/raw/`
- Verify filters aren't too restrictive
- Check session_id is being passed correctly
- Look at API response in Network tab

**Export CSV fails:**
- Check browser download settings
- Verify popup blocker isn't interfering
- Look for errors in console
- Try exporting smaller dataset first

**Pagination not working:**
- Check total row count in API response
- Verify `page` parameter is being sent
- Look for errors in console

### API Connection Issues

**All API calls return 404:**
```bash
# Verify frontend .env.local exists
cat frontend/.env.local
# Should contain: VUE_APP_BASE_URL=http://localhost:6500

# Restart frontend after creating .env.local
./stopapp.sh && ./runapp.sh

# Check where API calls are going
# DevTools → Network tab → Look at request URLs
# Should be: http://localhost:6500/api/*
# NOT: http://localhost:8080/api/*
```

**CORS errors:**
- Backend should have Flask-CORS installed
- Check `requirements.txt` includes `Flask-Cors~=4.0.0`
- Verify CORS is initialized in `backend/app/__init__.py`

**Timeout errors:**
- Large files may take time to process
- Check SSE connection in Network tab
- Increase timeout in `frontend/src/services/api.js`

### Session Issues

**Data persists when it shouldn't:**
```bash
# Clear browser localStorage
# DevTools → Application → Local Storage → Delete

# Or use incognito mode
```

**Can't see uploaded data:**
- Check session_id in localStorage
- Verify `{session_id}_sunburst_data.json` exists in `backend/data/`
- Try uploading in same browser/tab

### Performance Issues

**Large files process slowly:**
- This is normal for files > 50MB
- Watch progress messages in upload modal
- Consider sampling data first
- Check CPU usage during processing

**Chart lags when interacting:**
- Try Monochrome palette (faster rendering)
- Reduce hierarchy depth if possible
- Check browser performance (F12 → Performance tab)

### Viewing Logs

**Docker:**
```bash
# Follow logs in real-time
docker logs -f sunburst-csv-backend-1
docker logs -f sunburst-csv-frontend-1

# View last 100 lines
docker logs --tail 100 sunburst-csv-backend-1

# See all logs
docker compose logs
```

**Local:**
```bash
# Follow logs in real-time
tail -f backend.log
tail -f frontend.log

# View last 50 lines
tail -50 backend.log

# Search logs
grep "ERROR" backend.log
```

## Contributing

This project is actively maintained. Contributions are welcome!

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development notes:**
- Follow existing code style
- Add tests for new features
- Update README if adding new functionality
- Test both Docker and local development modes

## License

MIT License - See LICENSE file for details

## Credits

- **Original Concept**: Thomas M O'Neill
- **Development Assistance**: Claude Code by Anthropic
- **Visualization**: Apache ECharts
- **Framework**: Vue.js & Flask teams
- **Community**: All contributors and users

## Support

**Issues & Bugs:**
- Open an issue on GitHub: https://github.com/tmattoneill/sunburst-csv/issues
- Include browser console errors
- Attach sample data if possible (ensure no sensitive info)

**Feature Requests:**
- Open a discussion on GitHub
- Describe the use case
- Explain expected behavior

**Questions:**
- Check this README first
- Search existing GitHub issues
- Open a new issue with "Question:" prefix

---

**Built with ❤️ using Claude Code**
