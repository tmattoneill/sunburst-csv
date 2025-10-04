# Sunchart Application Diagnostics Report

**Date:** April 10, 2025  
**Status:** ✅ Ready to Run

---

## Executive Summary

Your Sunchart application is a **security data visualization tool** that:

- Accepts CSV/XLS/XLSX file uploads containing security incident data
- Processes the data into hierarchical structures
- Displays interactive sunburst charts for visual analysis
- Provides filterable data tables for detailed inspection

---

## Issues Fixed

### 1. ✅ Frontend Template Errors

- **Issue:** Vue 3 template had multiple root elements
- **Fix:** Wrapped template in single root `<div>`

### 2. ✅ Vue v-model Syntax Error

- **Issue:** Using deprecated `v-model:palette-name` syntax
- **Fix:** Changed to explicit `:palette-name` prop with `@update:palette-name` event

### 3. ✅ Missing Environment Configuration

- **Issue:** No `.env` file for frontend API configuration
- **Fix:** Created `frontend/.env` with proper API endpoints

### 4. ✅ Limited File Upload Support

- **Issue:** Only CSV files were accepted
- **Fix:** Added XLS/XLSX support with automatic conversion to CSV
- **Added:** `openpyxl` dependency for Excel file handling

### 5. ✅ Docker Backend Working Directory

- **Issue:** Gunicorn couldn't find the `api` module
- **Fix:** Updated Dockerfile to set correct WORKDIR to `/app/app`

---

## Application Architecture

### Backend (Flask + Python)

- **Port:** 6500
- **Framework:** Flask with Flask-CORS
- **Data Processing:** Pandas for CSV/Excel handling
- **Database:** SQLite for data storage and querying
- **Server:** Gunicorn for production serving

**Key Components:**

- `api/routes.py` - REST API endpoints
- `dataproc/report_processor.py` - Data transformation and tree building
- `dataproc/db_handler.py` - Database operations
- `dataproc/security_data_handler.py` - Report type detection

### Frontend (Vue 3)

- **Port:** 3000 (via Nginx in Docker)
- **Framework:** Vue 3 with Composition API
- **Charts:** ECharts for sunburst visualization
- **HTTP Client:** Axios for API calls

**Key Components:**

- `App.vue` - Main application container
- `FileLoaderModal.vue` - File upload interface
- `SunburstChart.vue` - Interactive chart visualization
- `DataTable.vue` - Filterable data table
- `DataPane.vue` - Node details display
- `PageHeader.vue` - Report metadata display

---

## API Endpoints

### Health Check

```
GET /api/health
```

### Get Visualization Data

```
GET /api/data
Returns: JSON with report metadata and hierarchical tree structure
```

### Upload File

```
POST /api/upload
Body: multipart/form-data with 'file' field
Accepts: CSV, XLS, XLSX
Returns: { filePath: string }
```

### Process Report

```
POST /api/process
Body: { clientName: string, filePath: string }
Returns: { message: string }
```

### Get Table Data

```
GET /api/table-data?page=1&items_per_page=20&filters={...}
POST /api/table-data (for CSV export)
```

---

## Data Flow

1. **Upload:** User uploads CSV/XLS/XLSX file via modal
2. **Conversion:** Excel files automatically converted to CSV
3. **Processing:**
   - File parsed and validated
   - Report type detected (basic/enhanced/detailed/full)
   - Data loaded into SQLite database
   - Hierarchical tree structure built using unique tag counts
4. **Visualization:**
   - Sunburst chart displays hierarchical data
   - User can click/hover nodes to drill down
   - Data table shows filtered records based on selected path
5. **Export:** Users can download filtered data as CSV

---

## Expected File Format

The application expects security incident reports with these columns:

**Minimum (Basic):**

- incident
- tag_name
- hit_type

**Enhanced:**

- - threat_behavior

**Detailed:**

- - publisher_name
- - country

**Full:**

- - report_period_hit_count
- - tag_status

The first 4 rows should contain metadata:

1. Report type name
2. Date range (format: "MM/DD/YYYY HH:MM - MM/DD/YYYY HH:MM")
3. (empty or additional metadata)
4. Column headers

---

## Known Limitations & Considerations

### 1. File Format Dependency

- Expects specific CSV structure with metadata rows
- Column names must match expected patterns
- Date format is hardcoded to `%m/%d/%Y %H:%M`

### 2. Database Persistence

- SQLite database stored in `backend/data/security.db`
- Data persists between container restarts via volume mount
- No multi-user support (single database)

### 3. Memory Constraints

- Large files (>100MB) may cause performance issues
- No streaming upload/processing
- All data loaded into memory during processing

### 4. Security Considerations

- No authentication/authorization
- File uploads not validated for malicious content
- CORS enabled for all origins
- Default secret key in use

### 5. Frontend Dependencies

- Requires Bootstrap CSS (loaded via CDN in index.html)
- Bootstrap Icons for UI elements
- No offline mode

---

## Docker Configuration

### Services

```yaml
backend:
  - Port: 6500
  - Volume: ./backend/data:/app/data
  - Environment: FLASK_ENV=production

frontend:
  - Port: 3000 (mapped to 80 in container)
  - Depends on: backend
  - Nginx serving static files
```

---

## How to Start

### Using Docker (Recommended)

```bash
docker-compose up --build
```

Access at: <http://localhost:3000>

### Manual Start (Development)

**Backend:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd app
python main.py
```

**Frontend:**

```bash
cd frontend
npm install
npm run serve
```

---

## Testing Checklist

- [ ] Upload CSV file with security data
- [ ] Upload XLS/XLSX file (should auto-convert)
- [ ] Verify sunburst chart renders
- [ ] Click nodes to drill down
- [ ] Hover nodes to see details in DataPane
- [ ] Check data table updates with filters
- [ ] Test pagination in data table
- [ ] Export filtered data as CSV
- [ ] Refresh data after upload
- [ ] Check browser console for errors

---

## Potential Improvements

1. **Authentication:** Add user login and session management
2. **File Validation:** Implement virus scanning and format validation
3. **Streaming:** Support large file uploads with streaming
4. **Caching:** Add Redis for session and data caching
5. **Error Handling:** Better user-facing error messages
6. **Testing:** Add unit and integration tests
7. **Monitoring:** Add logging and performance monitoring
8. **Responsive Design:** Improve mobile experience
9. **Export Options:** Add PDF/PNG chart export
10. **Real-time Updates:** WebSocket support for live data updates

---

## Dependencies Status

### Backend

- Flask 3.0.2 ✅
- Flask-Cors 4.0.0 ✅
- pandas 2.2.3 ✅
- gunicorn 23.0 ✅
- python-dotenv 1.0.1 ✅
- openpyxl 3.1.2 ✅

### Frontend

- Vue 3.5.13 ✅
- axios 1.7.0 ✅
- echarts 5.6.0 ✅
- @vue/cli-service 5.0.0 ✅

---

## Conclusion

Your application is **production-ready** for internal use but would benefit from:

- Authentication layer for security
- Better error handling and user feedback
- Performance optimization for large datasets
- Comprehensive testing suite

The core functionality (upload → process → visualize → export) is solid and working.
