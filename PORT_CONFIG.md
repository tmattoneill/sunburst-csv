# Port Configuration

This document defines the standardized port configuration across all deployment methods.

## Standard Port Assignments

### Local Development (runapp.sh)
- **Backend**: `6500`
- **Frontend**: `8080`

### Docker Compose
- **Backend**: `6500` (configurable via `BACKEND_PORT` in `.env.dev`)
- **Frontend**: `3000` (configurable via `FRONTEND_PORT` in `.env.dev`)

## Configuration Files

### Environment Variables

#### Root .env.dev (for runapp.sh and docker-compose)
```bash
FRONTEND_PORT=8080  # For local dev (runapp.sh)
BACKEND_PORT=6500   # For both local and Docker
```

#### Frontend .env.local (for Vue dev server)
```bash
VUE_APP_BASE_URL=http://localhost:6500  # Backend API URL
```

**Important**: The frontend needs its own `.env.local` file to tell Vue where the backend API is located. Without this, API calls will incorrectly target the frontend's own port (8080) instead of the backend (6500).

### runapp.sh
- Loads environment variables from `.env.dev`
- Uses `BACKEND_PORT` (defaults to 6500)
- Uses `FRONTEND_PORT` (defaults to 8080)
- All output messages display the actual configured ports

### docker-compose.yml
- Backend: Uses `${BACKEND_PORT:-6500}`
- Frontend: Uses `${FRONTEND_PORT:-3000}`
- Both use `.env.dev` for configuration

### Docker Files
- **backend/Dockerfile**: Uses `${FLASK_PORT:-6500}` from environment
- **frontend**: Nginx serves on port 80 internally, exposed via docker-compose port mapping

## Port Conflict Check

Before starting services, check if ports are available:

```bash
# Check backend port
lsof -i :6500

# Check frontend port (local dev)
lsof -i :8080

# Check frontend port (Docker)
lsof -i :3000
```

## Changing Ports

To change the default ports:

1. Edit `.env.dev`:
   ```bash
   FRONTEND_PORT=<your-port>
   BACKEND_PORT=<your-port>
   ```

2. Restart services:
   ```bash
   ./stopapp.sh
   ./runapp.sh
   ```

## Current Status

✅ **Consistency Achieved**:
- All scripts read from `.env.dev`
- All output messages reflect actual ports
- No hardcoded port values in startup scripts
- Docker and local dev can use different frontend ports without conflict
