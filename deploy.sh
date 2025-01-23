#!/bin/bash
set -eo pipefail

# Configuration
PROD_SERVER="moneill.net"
PROD_USER="ubuntu"
PROD_DIR="/home/ubuntu/docker/dataviz"
BACKUP_DIR="${PROD_DIR}/backups"
DRY_RUN=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true ;;
        -h|--help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --dry-run    Show what would happen without making changes"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Function to handle errors
cleanup() {
    local exit_code=$?
    echo "Cleaning up local files..."
    [ "$DRY_RUN" = false ] && rm -f deploy.tar.gz
    exit $exit_code
}

trap cleanup EXIT

# Function to execute or simulate commands
execute() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would execute: $*"
        return 0
    else
        "$@"
    fi
}

echo "Starting deployment to ${PROD_SERVER}..."
[ "$DRY_RUN" = true ] && echo "DRY RUN MODE - No changes will be made"

# 1. Create deployment package
echo "Creating deployment package..."
if [ "$DRY_RUN" = false ]; then
    git archive --format=tar.gz -o deploy.tar.gz HEAD || { echo "Failed to create deployment package"; exit 1; }
else
    echo "[DRY RUN] Would create git archive: deploy.tar.gz"
fi

# 2. Copy configuration files
echo "Copying configuration files..."
if [ "$DRY_RUN" = false ]; then
    scp deploy.tar.gz docker-compose.yml docker-compose.* .env "$PROD_USER@$PROD_SERVER:$PROD_DIR/" || { echo "Failed to copy files"; exit 1; }
else
    echo "[DRY RUN] Would copy files to $PROD_USER@$PROD_SERVER:$PROD_DIR/:"
    echo "  - deploy.tar.gz"
    echo "  - docker-compose.yml"
    echo "  - docker-compose.prod.yml"
    echo "  - .env.prod"
    echo "  - nginx.conf"
fi

# 3. SSH into server and deploy
if [ "$DRY_RUN" = false ]; then
    ssh $PROD_USER@$PROD_SERVER bash << EOF
        set -eo pipefail
        cd "${PROD_DIR}"

        # Create backup directory if it doesn't exist
        mkdir -p "${BACKUP_DIR}"

        # Explicitly load environment variables
        set -a  # automatically export all variables
        source .env.prod
        set +a

        # Verify environment variables are loaded
        echo "Checking environment variables:"
        echo "NODE_ENV: \${NODE_ENV}"
        echo "API_BASE_URL: \${API_BASE_URL}"
        echo "FLASK_PORT: \${FLASK_PORT}"
        echo "VUE_PORT: \${VUE_PORT}"
        sleep 30

        # Backup existing data
        if [ -d "data" ]; then
            echo "Backing up existing data..."
            backup_file="${BACKUP_DIR}/data-backup-\$(date +%Y%m%d_%H%M%S).tar.gz"
            tar -czf "\${backup_file}" data/ || { echo "Backup failed"; exit 1; }

            # Verify backup
            if [ ! -f "\${backup_file}" ]; then
                echo "Backup verification failed"
                exit 1
            fi
        fi

        # Extract new code
        echo "Extracting deployment package..."
        tar xzf deploy.tar.gz || { echo "Failed to extract deployment package"; exit 1; }

        # Set correct permissions
        echo "Setting permissions..."
        sudo chown -R ubuntu:ubuntu data/
        sudo chmod -R 755 data/

        # Stop existing containers
        echo "Stopping existing containers..."

        # Add build date to force cache invalidation
        export COMPOSE_ENVFILE=.env.prod
        export BUILD_DATE=$(date +%Y%m%d_%H%M%S)

        docker compose -f docker-compose.yml -f docker-compose.prod.yml down || true

        # Build and start new containers
        echo "Building and starting containers..."
        docker compose  -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
        docker compose  -f docker-compose.yml -f docker-compose.prod.yml up -d

        # Wait for health checks
        echo "Waiting for services to be healthy..."
        sleep 10
        if ! docker compose -f docker-compose.yml -f docker-compose.prod.yml ps | grep -q "healthy"; then
            echo "Services failed health check"
            docker compose -f docker-compose.yml -f docker-compose.prod.yml logs
            exit 1
        fi

        # Clean up
        echo "Cleaning up..."
        rm -f deploy.tar.gz

        echo "Deployment successful!"
EOF
else
    echo "[DRY RUN] Would execute on remote server:"
    echo "  - Create backup directory: $BACKUP_DIR"
    echo "  - Backup existing data to ${BACKUP_DIR}/data-backup-<timestamp>.tar.gz"
    echo "  - Extract deployment package"
    echo "  - Set permissions (owner: sunburst, mode: 755)"
    echo "  - Stop existing Docker containers"
    echo "  - Build and start new containers"
    echo "  - Verify service health"
    echo "  - Clean up temporary files"
fi

echo "Deployment $([ "$DRY_RUN" = true ] && echo "simulation ")complete!"