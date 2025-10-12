# Sunburst CSV

Interactive hierarchical data visualization tool for CSV and Excel files. Transform any tabular data with 3 or more nested categories into beautiful, explorable sunburst charts.

## Overview

Sunburst CSV is a full-stack web application that converts hierarchical CSV/XLSX data into interactive sunburst visualizations. Users upload their data, select columns for the hierarchy, choose a value metric, and instantly generate navigable charts with drill-down capabilities and detailed data tables.

Originally built for security report analysis, this tool has been generalized to handle any hierarchical dataset, making it useful for budget analysis, sales data, organizational structures, or any data with nested categories.

## Quick Start

### Prerequisites
- **Docker**: For containerized deployment
- **OR Local Development**: Python 3.11+ and Node.js 20+

### Option 1: Docker (Recommended for Production-like Testing)

```bash
# Clone and start
git clone https://github.com/tmattoneill/sunburst-csv.git
cd sunburst-csv
docker compose up --build
```

**Access at: http://localhost:3000**

To stop:
```bash
docker compose down
```

### Option 2: Local Development (Faster Iteration)

```bash
# Make scripts executable
chmod +x runapp.sh stopapp.sh

# Start both backend and frontend
./runapp.sh
```

**Access at: http://localhost:8080**

The script will:
- Create Python virtual environment (if needed)
- Install backend dependencies
- Install frontend dependencies (if needed)
- Create data directories
- Start both services in background

To stop:
```bash
./stopapp.sh
```

### Port Reference

| Service | Docker | Local Dev |
|---------|--------|-----------|
| Frontend | 3000 | 8080 |
| Backend | 6500 | 6500 |

See [PORT_CONFIG.md](PORT_CONFIG.md) for detailed port configuration.

## Key Features

### Data Processing
- Upload CSV or XLSX files up to any size
- Automatic column type detection (numeric vs text)
- Smart handling of currency symbols, commas, and percentages
- Support for missing data and NaN values
- Real-time preview of first 5 rows

### Visualization
- Interactive sunburst chart with smooth animations
- Click to drill down through hierarchy levels
- Hover to preview values without navigating
- Breadcrumb navigation to jump between levels
- Multiple color palettes (Ocean, Sunset, Forest, Monochrome)
- Responsive design for desktop and tablet

### Data Table
- Dynamic column generation from uploaded data
- Intelligent column ordering (hierarchy, value, other fields)
- Filter by current chart selection
- Pagination (20 rows per page)
- CSV export of filtered data
- Automatic formatting of column headers

### Workflow
- 4-step guided upload wizard
  1. Upload File - CSV or Excel
  2. Configure Hierarchy - Select and order 3+ columns
  3. Select Value Column - Choose numeric field to aggregate
  4. Name and Create - Set visualization title with real-time progress tracking
- Automatic modal on fresh start (no existing data)
- Column validation before processing
- Real-time progress bar with status messages
- Server-Sent Events for live processing updates
- Support for both generic mode and legacy security reports

## Usage Guide

### Basic Workflow

1. **Upload Data File**
   - On first load, the upload modal appears automatically
   - Or click the "Upload Data" button to manually open
   - Select your CSV or XLSX file
   - File must contain at least 3 columns for hierarchy
   - At least one column should contain numeric values

2. **Configure Hierarchy** (Step 2)
   - Select and order columns for hierarchy
   - Drag to reorder columns
   - Minimum 3 levels required
   - Example: Region > Department > Team

3. **Select Value Column** (Step 3)
   - Choose the numeric field to aggregate
   - Examples: revenue, count, hours, budget

4. **Name and Create** (Step 4)
   - Name your visualization
   - Click "Create"
   - Watch real-time progress bar as data processes
   - See status messages for each processing step
   - Large files show row-by-row progress

5. **Explore Your Chart**
   - **Click** segments to drill down
   - **Hover** segments to see details
   - Use breadcrumbs to navigate up
   - View detailed data in the table below

6. **Analyze Data**
   - Data table shows filtered records based on selection
   - Use pagination to browse records
   - Export filtered data as CSV

### Example Datasets

**Marketing Spend:**
- Hierarchy: dsp_name > brand_name > buyer_name
- Value: ad_spend
- Shows advertising budget across platforms and brands

**Sales Data:**
- Hierarchy: region > product_category > product_name
- Value: revenue
- Reveals sales distribution by geography and product

**Budget Allocation:**
- Hierarchy: department > project > expense_category
- Value: amount
- Displays organizational spending patterns

## Technology Stack

### Backend
- Python 3.11
- Flask web framework with Server-Sent Events
- Pandas for data processing
- Gunicorn production server
- SQLite for legacy mode
- Session-based data isolation

### Frontend
- Vue 3 with Composition API
- ECharts for sunburst visualization
- Bootstrap 5 for UI components
- Fetch API for streaming progress
- localStorage for session management

### Deployment
- Docker containerization
- Docker Compose orchestration
- Nginx for frontend serving
- Hot reload in development mode

## Session Management

The application uses browser localStorage to maintain isolated sessions per user. Each session gets a unique ID that persists across page reloads but is cleared when:
- localStorage is cleared
- Using incognito/private mode
- Using a different browser

Session data files are stored as `{session_id}_sunburst_data.json` on the backend, preventing data conflicts between users.

To start completely fresh:
- Clear browser localStorage (DevTools > Application > Local Storage)
- Or use incognito/private browsing mode
- The upload modal will automatically appear when no data exists

## Project Structure

```
sunburst-csv/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoints
│   │   ├── dataproc/
│   │   │   ├── generic_processor.py   # CSV/XLSX processing
│   │   │   ├── report_processor.py    # Legacy security reports
│   │   │   └── db_handler.py          # Database operations
│   │   └── main.py                # Flask application
│   ├── data/
│   │   ├── raw/                   # Uploaded files
│   │   └── *.json                 # Session visualization data
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SunburstChart.vue      # ECharts visualization
│   │   │   ├── FileLoaderModal.vue    # Upload wizard
│   │   │   ├── ColumnSelector.vue     # Hierarchy builder
│   │   │   ├── DataTable.vue          # Tabular data display
│   │   │   ├── DataPane.vue           # Summary statistics
│   │   │   └── PageHeader.vue         # Navigation breadcrumbs
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   └── App.vue                # Root component
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── runapp.sh                      # Local development startup
├── stopapp.sh                     # Stop local services
├── .env.dev                       # Port configuration
├── PORT_CONFIG.md                 # Port documentation
├── CLAUDE.md                      # Development documentation
└── README.md                      # This file
```

## API Reference

### Upload File

```
POST /api/upload
Content-Type: multipart/form-data

Parameters:
  - file: CSV or XLSX file
  - session_id: (optional) Session identifier

Response:
  - filePath: string (saved filename)
```

### Get File Info

```
GET /api/file-info?filePath=filename.csv&session_id=xxx

Response:
  - columns: array of column metadata
  - rowCount: total rows in file
  - preview: first 5 rows
  - fileName: original filename
```

### Validate Columns

```
POST /api/validate-columns
Content-Type: application/json

Body:
  - filePath: string
  - treeOrder: array of column names
  - valueColumn: string
  - session_id: string

Response:
  - valid: boolean
  - errors: array of error messages
```

### Process File

```
POST /api/process
Content-Type: application/json

Body (Generic Mode):
  - filePath: string
  - chartName: string
  - treeOrder: array of column names
  - valueColumn: string
  - session_id: string

Response:
  - Server-Sent Events stream with progress updates
  - Final message: success confirmation
```

### Get Chart Data

```
GET /api/data?session_id=xxx

Response:
  - chart_name: string
  - tree_order: array
  - value_column: string
  - source_file: string
  - data: nested tree structure
```

### Get Table Data

```
GET /api/table-data?page=1&items_per_page=20&session_id=xxx

Optional Parameters:
  - filters: JSON object of column filters

Response:
  - data: array of row objects
  - page: current page number
  - total: total rows
  - total_pages: total pages
```

### Health Check

```
GET /api/health

Response:
  - status: "healthy"
```

## Configuration

### Environment Variables

See [PORT_CONFIG.md](PORT_CONFIG.md) for complete port configuration documentation.

**Backend** (.env.dev):
- `BACKEND_PORT`: Backend server port (default: 6500)
- `DATA_DIR`: Base directory for data files
- `UPLOAD_DIR`: Directory for uploaded files
- `DATABASE_URL`: SQLite database path (legacy mode)

**Frontend** (.env.local for local dev):
- `VUE_APP_BASE_URL`: Backend API URL (default: http://localhost:6500)

**Frontend** (.env.production for Docker):
- `VUE_APP_BASE_URL`: Backend API URL

## Development

### Backend Development

```bash
cd backend/app
source ../venv/bin/activate
pip install -r ../requirements.txt
python main.py  # Runs on port 6500
```

### Frontend Development

```bash
cd frontend
npm install
npm run serve  # Runs on port 8080
npm run build  # Production build
npm run lint   # Lint code
```

### Code Structure

**Generic Processor Pipeline:**
1. Read CSV/XLSX file
2. Validate columns exist and have correct types
3. Clean numeric values (remove currency, commas)
4. Build tree recursively by grouping and summing
5. Generate metadata with tree_order and value_column
6. Save to `{session_id}_sunburst_data.json`

**Frontend State Management:**
1. FileLoaderModal handles upload and column selection
2. App.vue fetches chart data and manages navigation
3. SunburstChart renders visualization and emits events
4. DataTable queries filtered data based on current path
5. All components react to path changes via props

## Data Format

### Input CSV Structure

```csv
category_a,category_b,category_c,amount,other_field
Region1,Dept1,Team1,1000,notes
Region1,Dept1,Team2,1500,notes
Region1,Dept2,Team3,2000,notes
Region2,Dept3,Team4,2500,notes
```

### Output Tree Structure

```json
{
  "chart_name": "Budget Analysis",
  "tree_order": ["category_a", "category_b", "category_c"],
  "value_column": "amount",
  "source_file": "budget-20251004-120000.csv",
  "data": {
    "name": "Budget Analysis",
    "value": 7000,
    "children": [
      {
        "name": "Region1",
        "value": 4500,
        "children": [
          {
            "name": "Dept1",
            "value": 2500,
            "children": [
              {"name": "Team1", "value": 1000, "children": []},
              {"name": "Team2", "value": 1500, "children": []}
            ]
          }
        ]
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
docker compose up --build
```

**Can't access frontend:**
- Check: http://localhost:3000
- Verify containers are running: `docker ps`
- Check logs: `docker logs sunburst-csv-frontend-1`

### Local Development Issues

**Backend won't start:**
- Check logs: `tail -f backend.log`
- Verify Python 3.x is installed: `python3 --version`
- Check if port 6500 is in use: `lsof -i :6500`
- Look for errors in `backend.log`

**Frontend won't start:**
- Check logs: `tail -f frontend.log`
- Verify Node.js is installed: `node --version`
- Check if port 8080 is in use: `lsof -i :8080`
- Delete `node_modules` and reinstall: `npm install`

**Services still running after stopapp.sh:**
```bash
./stopapp.sh
# Or manually:
pkill -f gunicorn
pkill -f "npm run serve"
pkill -f "vue-cli-service"
```

### Upload Issues

**Upload fails:**
- Check file format matches requirements (CSV or XLSX)
- Ensure file size is reasonable (under 100MB recommended)
- Verify file has valid headers in first row
- Check backend logs for specific errors

**No columns appear in hierarchy selector:**
- Confirm file uploaded successfully
- Check browser console for API errors (F12)
- Verify backend is running on port 6500
- Test backend health: `curl http://localhost:6500/api/health`

### Chart Issues

**Chart not rendering:**
- Check browser console for errors (F12)
- Confirm data exists in backend (check API response)
- Verify API calls are going to port 6500, not 8080
- Try refreshing the page (hard refresh: Cmd+Shift+R)
- Check if `/api/data?session_id=xxx` endpoint returns data

**DataTable shows no rows:**
- Ensure you have processed a file first
- Check that source CSV still exists in `backend/data/raw/`
- Verify filters are not too restrictive
- Check session_id is being passed correctly

### API Connection Issues

**404 errors on API calls:**
- Verify `frontend/.env.local` exists with `VUE_APP_BASE_URL=http://localhost:6500`
- Restart frontend after creating/modifying `.env.local`
- Check Network tab in browser DevTools to see where API calls are going
- Backend should be running on port 6500

### Viewing Logs

**Docker:**
```bash
docker logs sunburst-csv-backend-1
docker logs sunburst-csv-frontend-1
docker logs -f sunburst-csv-backend-1  # Follow mode
```

**Local:**
```bash
tail -f backend.log
tail -f frontend.log
```

## Contributing

This project was developed with assistance from Claude Code. For bug reports or feature requests, please open an issue on GitHub.

## License

MIT License - See LICENSE file for details

## Credits

Built with Claude Code by Anthropic
Original concept and development by Thomas M O'Neill
