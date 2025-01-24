#!/usr/bin/env bash

# Set environment file
ENV_FILE=".env"
COMPOSE_FILES="-f docker-compose.yml"
COMPOSE_CMD="docker compose --env-file $ENV_FILE $COMPOSE_FILES"
COMPOSE_OPTIONS="--build -d"

# Function to check if the environment file exists
check_env_file() {
    if [[ ! -f "$ENV_FILE" ]]; then
        echo "Error: Environment file '$ENV_FILE' not found!"
        exit 1
    fi
}

# Function to stop the dev environment if running
stop_dev_environment() {
    echo "Stopping development environment if running..."
    docker-compose down
}

# Function to check if prod containers are running
is_running() {
    $COMPOSE_CMD ps --services --filter "status=running" | grep -q .
}

# Function to validate production configuration
validate_config() {
    echo "Validating production configuration..."
    $COMPOSE_CMD config
    if [[ $? -ne 0 ]]; then
        echo "Error: Configuration validation failed!"
        exit 1
    fi
}

# Function to bring up production containers
start_containers() {
    if is_running; then
        echo "Production containers are already running."
    else
        stop_dev_environment
        validate_config
        echo "Building and starting production containers..."
        $COMPOSE_CMD build
        if [[ $? -ne 0 ]]; then
            echo "Error: Docker build failed!"
            exit 1
        fi
        $COMPOSE_CMD up "$COMPOSE_OPTIONS"
        echo "Production containers started successfully."
    fi
}

# Function to stop production containers
stop_containers() {
    if is_running; then
        echo "Stopping production containers..."
        $COMPOSE_CMD down
        echo "Production containers stopped successfully."
    else
        echo "Production containers are not running."
    fi
}

# Main script logic
case "$1" in
    up)
        check_env_file
        start_containers
        ;;
    down)
        check_env_file
        stop_containers
        ;;
    *)
        echo "Usage: $0 {up|down}"
        exit 1
        ;;
esac
