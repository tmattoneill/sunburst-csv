#!/bin/bash

# Get the script's directory (works on both macOS and Linux)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

VENV_DIR="$SCRIPT_DIR/backend/venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/backend/requirements.txt"
BACKEND_DIR="$SCRIPT_DIR/backend/app"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
DATA_DIR="$SCRIPT_DIR/backend/data"

echo "🚀 Starting Sunchart services..."
echo ""

# ============================================
# BACKEND SETUP
# ============================================

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment not found."
    echo "🔧 Creating virtual environment..."

    python3 -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment."
        exit 1
    fi

    echo "✅ Virtual environment created."
fi

# Activate virtual environment
echo "🔹 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: Failed to activate virtual environment."
    exit 1
fi

# Install/update Python dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --quiet -r "$REQUIREMENTS_FILE"

    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies."
        exit 1
    fi

    echo "✅ Python dependencies installed."
else
    echo "⚠️  Warning: requirements.txt not found."
fi

# ============================================
# FRONTEND SETUP
# ============================================

PACKAGE_JSON="$FRONTEND_DIR/package.json"
PACKAGE_LOCK="$FRONTEND_DIR/package-lock.json"
NODE_MODULES="$FRONTEND_DIR/node_modules"

# Check if we need to run npm install
NEED_NPM_INSTALL=false

if [ ! -d "$NODE_MODULES" ]; then
    echo "⚠️  node_modules not found."
    NEED_NPM_INSTALL=true
elif [ "$PACKAGE_JSON" -nt "$NODE_MODULES" ]; then
    echo "⚠️  package.json is newer than node_modules."
    NEED_NPM_INSTALL=true
elif [ -f "$PACKAGE_LOCK" ] && [ "$PACKAGE_LOCK" -nt "$NODE_MODULES" ]; then
    echo "⚠️  package-lock.json is newer than node_modules."
    NEED_NPM_INSTALL=true
fi

if [ "$NEED_NPM_INSTALL" = true ]; then
    echo "📦 Installing/updating frontend dependencies..."
    cd "$FRONTEND_DIR"
    npm install

    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install frontend dependencies."
        exit 1
    fi

    echo "✅ Frontend dependencies installed."
else
    echo "✅ Frontend dependencies up to date."
fi

# ============================================
# ENVIRONMENT SETUP
# ============================================

# Create data directories if they don't exist
mkdir -p "$DATA_DIR/raw"
mkdir -p "$DATA_DIR/processed"

# Set environment variables for the backend
export OPENBLAS_NUM_THREADS=1
export OPENBLAS_L2_SIZE=512
export FLASK_PORT=6500
export FLASK_DEBUG=0
export DATA_DIR="$DATA_DIR"
export UPLOAD_DIR="$DATA_DIR/raw"
export DATABASE_URL="$DATA_DIR/security.db"
export DATA_PATH="$DATA_DIR"

echo ""
echo "🔹 Environment configured:"
echo "   - Backend: http://0.0.0.0:6500"
echo "   - Frontend: http://localhost:8080 (Vue dev server)"
echo "   - Data directory: $DATA_DIR"
echo ""

# ============================================
# START SERVICES
# ============================================

# Start the Flask backend server
echo "🔹 Starting Flask backend..."
cd "$BACKEND_DIR"
nohup gunicorn --bind 0.0.0.0:6500 "api:create_app()" > "$SCRIPT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

if [ $? -eq 0 ]; then
    echo "✅ Backend started (PID: $BACKEND_PID)"
    echo "   Log: $SCRIPT_DIR/backend.log"
else
    echo "❌ Error: Failed to start backend."
    exit 1
fi

# Wait a moment for backend to start
sleep 2

# Start the Vue frontend dev server
echo "🔹 Starting Vue frontend..."
cd "$FRONTEND_DIR"
nohup npm run serve > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

if [ $? -eq 0 ]; then
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
    echo "   Log: $SCRIPT_DIR/frontend.log"
else
    echo "❌ Error: Failed to start frontend."
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo "🚀 All services started successfully!"
echo ""
echo "📝 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "🛑 To stop services, run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📊 Access the application:"
echo "   Frontend: http://localhost:8080"
echo "   Backend:  http://localhost:6500/api/health"
echo ""

exit 0
