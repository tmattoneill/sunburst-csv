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

# Launch the Python API
log "Starting Python API..."
cd api || exit
python3 api.py &
API_PID=$!
log "Python API started with PID $API_PID"

# Handle Node.js frontend
log "Switching to Node.js frontend..."
cd ../frontend || exit

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

# Function to clean up processes on exit
cleanup() {
  echo "Stopping processes..."
  kill $API_PID $FRONTEND_PID 2>/dev/null
  wait $API_PID $FRONTEND_PID 2>/dev/null
  echo "All processes stopped. Returning to home directory."
}

# Trap SIGINT (CTRL-C) and EXIT to clean up processes
trap cleanup SIGINT EXIT

# Wait for the processes to keep running
wait

# Ensure returning to the original directory after exiting
cd "$HOME_DIR" || exit
log "Returned to $HOME_DIR"
