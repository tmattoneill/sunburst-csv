#!/usr/bin/env bash

# Set environment file
ENV_FILE=".env"
COMPOSE_CMD="docker compose --env-file $ENV_FILE"

# Check if the environment file exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: Environment file '$ENV_FILE' not found!"
    exit 1
fi

# Function to check if any service is running
is_running() {
    $COMPOSE_CMD ps --services --filter "status=running" | grep -q .
}

# Function to bring up the containers
start_containers() {
    if is_running; then
        echo "Containers are already running."
    else
        echo "Building and starting Docker containers..."
        $COMPOSE_CMD build --no-cache
        $COMPOSE_CMD up --remove-orphans -d
        if [[ $? -ne 0 ]]; then
            echo "Error: Docker up command failed!"
            exit 1
        fi
        echo "Containers started successfully."
    fi
}

# Function to stop the containers
stop_containers() {
    if is_running; then
        echo "Stopping Docker containers..."
        $COMPOSE_CMD down
        echo "Containers stopped successfully."
    else
        echo "Containers are not running."
    fi
}

# Main script logic
case "$1" in
    up)
        start_containers
        ;;
    down)
        stop_containers
        ;;
    *)
        echo "Usage: $0 {up|down}"
        exit 1
        ;;
esac
