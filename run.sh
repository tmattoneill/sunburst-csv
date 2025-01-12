#!/bin/bash

# File to store the last known machine ID
MACHINE_ID_FILE=".machine_id"

# Store cwd
HOME_DIR=$(pwd)

# Function to get the current machine's MAC address or hostname
get_machine_id() {
  if command -v ifconfig >/dev/null 2>&1; then
    # Use ifconfig for MAC address (Unix-based systems)
    ifconfig | grep -m 1 ether | awk '{print $2}'
  else
    # Fallback to hostname
    hostname
  fi
}

# Store current machine ID
CURRENT_MACHINE_ID=$(get_machine_id)

# Check if the machine ID has changed
if [ -f "$MACHINE_ID_FILE" ]; then
  LAST_MACHINE_ID=$(cat "$MACHINE_ID_FILE")
else
  LAST_MACHINE_ID=""
fi

# Save the current machine ID
echo "$CURRENT_MACHINE_ID" > "$MACHINE_ID_FILE"

# Function to log messages
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to clean up processes
cleanup() {
  echo "Stopping processes..."
  
  # Send SIGTERM first to allow graceful shutdown
  if [ ! -z "$API_PID" ]; then
    kill -TERM $API_PID 2>/dev/null
    sleep 1
    # If process still exists, force kill
    if kill -0 $API_PID 2>/dev/null; then
      kill -9 $API_PID 2>/dev/null
    fi
  fi
  
  if [ ! -z "$FRONTEND_PID" ]; then
    kill -TERM $FRONTEND_PID 2>/dev/null
    sleep 1
    if kill -0 $FRONTEND_PID 2>/dev/null; then
      kill -9 $FRONTEND_PID 2>/dev/null
    fi
  fi
  
  # Wait for processes to finish
  wait $API_PID $FRONTEND_PID 2>/dev/null
  
  echo "All processes stopped. Returning to home directory."
  cd "$HOME_DIR" || exit
  log "Returned to $HOME_DIR"
}

# Trap SIGINT (CTRL-C), SIGTERM, and EXIT
trap cleanup SIGINT SIGTERM EXIT

# Launch the Python API with proper shutdown handling
log "Starting Python API..."

# Start the API in the background
python3 app/main.py &
API_PID=$!
log "Python API started with PID $API_PID"

# Function to handle shutdown
function shutdown() {
    log "Shutting down Python API with PID $API_PID"
    kill -SIGTERM "$API_PID"
    wait "$API_PID"
    log "Python API stopped"
    exit 0
}

# Trap signals and execute shutdown function
trap shutdown SIGINT SIGTERM

# Wait for the API process to finish
wait "$API_PID"


# Handle Node.js frontend
log "Switching to Node.js frontend..."
cd frontend || exit

if [ "$CURRENT_MACHINE_ID" != "$LAST_MACHINE_ID" ]; then
  log "Machine ID has changed. Cleaning and rebuilding the frontend..."
  if [ -d "node_modules" ]; then
    rm -rf node_modules
    log "Removed node_modules."
  fi
  if [ -f "package-lock.json" ]; then
    rm package-lock.json
    log "Removed package-lock.json."
  fi
  npm install
  log "Rebuilt the frontend."
else
  log "Machine ID has not changed. Skipping frontend rebuild."
fi

# Run the frontend
log "Starting frontend development server..."
npm run serve &
FRONTEND_PID=$!
log "Frontend server started with PID $FRONTEND_PID"

# Wait for the processes to keep running
wait