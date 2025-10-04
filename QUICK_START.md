# Sunchart Quick Start Guide

## Start the Application

```bash
docker-compose up --build
```

Then open: **http://localhost:3000**

---

## How to Use

### 1. Upload Data File
- Click the upload button (should be visible in the UI)
- Select a CSV, XLS, or XLSX file
- Enter a client name
- Click "Upload"

### 2. View Visualization
- Sunburst chart displays hierarchical security data
- **Click** nodes to drill down
- **Hover** nodes to see details
- Use breadcrumb path to navigate back up

### 3. Analyze Data
- Data table below chart shows filtered records
- Table updates based on selected chart node
- Use pagination to browse records
- Export filtered data as CSV

### 4. Refresh
- Click refresh button to reload data after new upload

---

## File Format Requirements

Your CSV/Excel file should have:

**First 4 rows (metadata):**
1. Report type name
2. Date range: "MM/DD/YYYY HH:MM - MM/DD/YYYY HH:MM"
3. (empty or metadata)
4. Column headers

**Required columns:**
- incident
- tag_name
- hit_type

**Optional columns (for richer visualization):**
- threat_behavior
- publisher_name
- country
- malware_condition
- named_threat
- etc.

---

## Troubleshooting

### Containers won't start
```bash
docker-compose down
docker-compose up --build
```

### Can't access frontend
- Check: http://localhost:3000
- Verify containers are running: `docker ps`

### Upload fails
- Check file format matches requirements
- Ensure file has required columns
- Check backend logs: `docker logs sunchart-backend-1`

### Chart not rendering
- Check browser console for errors (F12)
- Verify data file was processed successfully
- Check if `/api/data` endpoint returns data

---

## Stop the Application

```bash
docker-compose down
```

To also remove volumes (clears database):
```bash
docker-compose down -v
```
