#!/usr/bin/env bash

# Set environment file
ENV_FILE=".env.dev"

# Check if the environment file exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: Environment file '$ENV_FILE' not found!"
    exit 1
fi

# Build and start the Docker containers
echo "Building Docker containers..."
docker-compose --env-file "$ENV_FILE" build

if [[ $? -ne 0 ]]; then
    echo "Error: Docker build failed!"
    exit 1
fi

echo "Starting Docker containers..."
docker-compose --env-file "$ENV_FILE" up --remove-orphans
