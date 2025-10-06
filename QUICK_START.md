# Sunchart Quick Start Guide

## Start the Application

### Option 1: Docker (Recommended for Production-like Testing)

```bash
docker-compose up -d --build
```

Then open: **http://localhost:3000**

To stop:
```bash
docker-compose down
```

### Option 2: Local Development (Faster Iteration)

```bash
chmod +x runapp.sh stopapp.sh
./runapp.sh
```

Then open: **http://localhost:8080**

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

### Docker Issues

**Containers won't start:**
```bash
docker-compose down
docker-compose up --build
```

**Can't access frontend:**
- Check: http://localhost:3000
- Verify containers are running: `docker ps`

### Local Development Issues

**Backend won't start:**
- Check logs: `tail -f backend.log`
- Verify Python 3.x is installed: `python3 --version`
- Check if port 6500 is in use: `lsof -i :6500`

**Frontend won't start:**
- Check logs: `tail -f frontend.log`
- Verify Node.js is installed: `node --version`
- Check if port 8080 is in use: `lsof -i :8080`

**Services still running:**
```bash
./stopapp.sh
# Or manually:
pkill -f gunicorn
pkill -f "npm run serve"
```

### Upload Issues

**Upload fails:**
- Check file format matches requirements
- Ensure file has required columns
- Check backend logs for errors

### Chart Issues

**Chart not rendering:**
- Check browser console for errors (F12)
- Verify data file was processed successfully
- Check if `/api/data` endpoint returns data

---

## Port Reference

| Service | Docker Port | Local Port |
|---------|-------------|------------|
| Frontend | 3000 | 8080 |
| Backend | 6500 | 6500 |

---

## Logs

**Docker:**
```bash
docker logs sunchart-backend-1
docker logs sunchart-frontend-1
```

**Local:**
```bash
tail -f backend.log
tail -f frontend.log
```
