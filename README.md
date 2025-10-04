# Sunburst CSV

Interactive hierarchical data visualization tool for CSV and Excel files. Transform any tabular data with 3 or more nested categories into beautiful, explorable sunburst charts.

## Overview

Sunburst CSV is a full-stack web application that converts hierarchical CSV/XLSX data into interactive sunburst visualizations. Users upload their data, select columns for the hierarchy, choose a value metric, and instantly generate navigable charts with drill-down capabilities and detailed data tables.

Originally built for security report analysis, this tool has been generalized to handle any hierarchical dataset, making it useful for budget analysis, sales data, organizational structures, or any data with nested categories.

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

## Installation

### Prerequisites
- Docker and Docker Compose
- Git

### Quick Start

Clone the repository:

```bash
git clone https://github.com/tmattoneill/sunburst-csv.git
cd sunburst-csv
```

Start the application:

```bash
docker compose up --build
```

Access the application at http://localhost:3000

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

## Usage Guide

### Basic Workflow

1. On first load, the upload modal appears automatically
   - Or click the Upload Data button to manually open

2. Step 1: Select your CSV or XLSX file
   - File must contain at least 3 columns for hierarchy
   - At least one column should contain numeric values

3. Step 2: Configure your hierarchy by selecting columns in order
   - Drag to reorder columns
   - Minimum 3 levels required
   - Example: Region > Department > Team

4. Step 3: Choose your value column
   - Select the numeric field to aggregate
   - Examples: revenue, count, hours, budget

5. Step 4: Name your visualization and click Create
   - Watch real-time progress bar as data processes
   - See status messages for each processing step
   - Large files show row-by-row progress

6. Explore your chart
   - Click segments to drill down
   - Use breadcrumbs to navigate up
   - Hover for quick value previews
   - View detailed data in the table below

### Example Datasets

Marketing Spend:
- Hierarchy: dsp_name > brand_name > buyer_name
- Value: ad_spend
- Shows advertising budget across platforms and brands

Sales Data:
- Hierarchy: region > product_category > product_name
- Value: revenue
- Reveals sales distribution by geography and product

Budget Allocation:
- Hierarchy: department > project > expense_category
- Value: amount
- Displays organizational spending patterns

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
│   │   └── sunburst_data.json     # Generated visualization data
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
├── CLAUDE.md                      # Development documentation
├── ERRORS.md                      # Bug fixes log
└── README.md
```

## API Reference

### Upload File

```
POST /api/upload
Content-Type: multipart/form-data

Parameters:
  - file: CSV or XLSX file

Response:
  - filePath: string (saved filename)
```

### Get File Info

```
GET /api/file-info?filePath=filename.csv

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

Response:
  - message: success confirmation
```

### Get Chart Data

```
GET /api/data

Response:
  - chart_name: string
  - tree_order: array
  - value_column: string
  - source_file: string
  - data: nested tree structure
```

### Get Table Data

```
GET /api/table-data?page=1&items_per_page=20

Optional Parameters:
  - filters: JSON object of column filters

Response:
  - data: array of row objects
  - page: current page number
  - total: total rows
  - total_pages: total pages
```

## Configuration

### Environment Variables

Backend:
- DATA_DIR: Base directory for data files (default: ../data)
- UPLOAD_DIR: Directory for uploaded files (default: ../data/raw)
- DATABASE_URL: SQLite database path (default: ../data/security.db)
- FLASK_PORT: Backend server port (default: 6500)

Frontend:
- VUE_APP_API_ROOT_PATH: API base path (default: /api)
- VUE_APP_BASE_URL: Backend URL (default: http://localhost:6500)

### Docker Compose

Ports:
- Frontend: 3000 (nginx)
- Backend: 6500 (gunicorn)

Volumes:
- ./backend/app:/app/app (backend code)
- ./backend/data:/app/data (data persistence)
- ./frontend/src:/app/src (frontend code)

## Development

### Backend Development

Run Flask in debug mode:

```bash
cd backend/app
python main.py
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Frontend Development

Run Vue dev server:

```bash
cd frontend
npm install
npm run serve
```

Build for production:

```bash
npm run build
```

### Code Structure

Generic Processor Pipeline:
1. Read CSV/XLSX file
2. Validate columns exist and have correct types
3. Clean numeric values (remove currency, commas)
4. Build tree recursively by grouping and summing
5. Generate metadata with tree_order and value_column
6. Save to sunburst_data.json

Frontend State Management:
1. FileLoaderModal handles upload and column selection
2. App.vue fetches chart data and manages navigation
3. SunburstChart renders visualization and emits events
4. DataTable queries filtered data based on current path
5. All components react to path changes via props

## Data Format

### Input CSV Structure

```
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

### Common Issues

File upload fails with 400 error:
- Check file is CSV or XLSX format
- Ensure file size is reasonable (under 100MB recommended)
- Verify file has valid headers in first row

No columns appear in hierarchy selector:
- Confirm file uploaded successfully
- Check browser console for API errors
- Verify backend is running on port 6500

DataTable shows no rows:
- Ensure you have processed a file first
- Check that source CSV still exists in data/raw
- Verify filters are not too restrictive

Chart does not render:
- Confirm data exists in sunburst_data.json
- Check for JavaScript errors in browser console
- Try refreshing the page

### Debug Mode

Enable backend logging:

```python
# backend/app/main.py
app.run(debug=True, port=6500)
```

Enable Vue devtools:

```javascript
// frontend/vue.config.js
module.exports = {
  productionSourceMap: true
}
```

## Contributing

This project was developed with assistance from Claude Code. For bug reports or feature requests, please open an issue on GitHub.

## License

MIT License - See LICENSE file for details

## Credits

Built with Claude Code by Anthropic
Original concept and development by Thomas M O'Neill
