#!/bin/bash

VENV_DIR="./backend/venv"
REQUIREMENTS_FILE="./backend/requirements.txt"

echo "🚀 Starting Sunchart services..."
sleep 1

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment not found at $VENV_DIR."
    echo "🔧 Creating virtual environment in ./backend..."

    # Create the virtual environment
    python3 -m venv "$VENV_DIR"

    # Check if venv creation was successful
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment."
        exit 1
    fi

    echo "✅ Virtual environment created successfully."

    # Activate the new virtual environment
    echo "🔹 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"

    # Confirm activation
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "❌ Error: Failed to activate virtual environment."
        exit 1
    fi

    # Install dependencies
    if [ -f "$REQUIREMENTS_FILE" ]; then
        echo "📦 Installing dependencies from requirements.txt..."
        pip install -r "$REQUIREMENTS_FILE"

        # Check if pip install was successful
        if [ $? -ne 0 ]; then
            echo "❌ Error: Failed to install dependencies."
            exit 1
        fi

        echo "✅ Dependencies installed successfully."
    else
        echo "⚠️  Warning: requirements.txt not found. Skipping dependency installation."
    fi
else
    # Activate the existing virtual environment
    echo "🔹 Activating virtual environment..."
    source "$VENV_DIR/bin/activate"

    # Confirm activation
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "❌ Error: Failed to activate virtual environment."
        exit 1
    fi
fi

sleep 1

# Set environment variables for the backend
export OPENBLAS_NUM_THREADS=1
export OPENBLAS_L2_SIZE=512

# Start the Flask backend server
HOST=0.0.0.0
FLASK_PORT=6500
BACKEND_DIR="/home/ubuntu/sunchart/backend/app"

echo "🔹 Starting Flask backend server..."
if cd "$BACKEND_DIR"; then
    nohup gunicorn --bind ${HOST}:${FLASK_PORT} "api:create_app()" > /home/ubuntu/sunchart/backend.log 2>&1 &
    if [ $? -eq 0 ]; then
        echo "✅ Flask backend started successfully on port $FLASK_PORT."
    else
        echo "❌ Error: Failed to start Flask backend."
        exit 1
    fi
else
    echo "❌ Error: Backend directory not found: $BACKEND_DIR"
    exit 1
fi

# Start the Vue frontend dev server
FRONTEND_DIR="/home/ubuntu/sunchart/frontend"
sleep 3
echo "🔹 Starting Vue frontend server..."
if cd "$FRONTEND_DIR"; then
    nohup npm run serve > /home/ubuntu/sunchart/frontend.log 2>&1 &
    if [ $? -eq 0 ]; then
        echo "✅ Vue frontend started successfully."
    else
        echo "❌ Error: Failed to start Vue frontend."
        exit 1
    fi
else
    echo "❌ Error: Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi
sleep 2
echo "🚀 All services started successfully!"
exit 0
