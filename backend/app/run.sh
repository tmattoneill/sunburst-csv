#!/usr/bin/bash

export OPENBLAS_NUM_THREADS=1   # If you want to limit CPU threads
export OPENBLAS_L2_SIZE=512     # Set a reasonable L2 cache size (adjust as needed)

HOST=0.0.0.0
FLASK_PORT=6500

echo "Loading API..."
gunicorn --bind ${HOST}:${FLASK_PORT} "api:create_app()" &
