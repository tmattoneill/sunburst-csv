#!/bin/bash
set -eo pipefail

# Configuration
PROD_SERVER="moneill.net"
PROD_USER="ubuntu"
PROD_DIR="/home/ubuntu/docker/dataviz"
DEPLOY_BRANCH="remote-prod"
LOG_FILE="deploy.log"
DRY_RUN=false

# Function definitions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a $LOG_FILE
}

execute() {
    if [ "$DRY_RUN" = true ]; then
        log "[DRY RUN] Would execute: $*"
        return 0
    else
        "$@"
    fi
}

check_branch() {
    local current_branch=$(execute git branch --show-current)
    if [ "$current_branch" != "$DEPLOY_BRANCH" ]; then
        log "ERROR: Not on $DEPLOY_BRANCH branch"
        exit 1
    fi
}

create_deployment_package() {
    log "Creating deployment package..."
    execute git archive --format=tar.gz -o deploy.tar.gz HEAD
}

copy_files() {
    log "Copying configuration files..."
    execute scp deploy.tar.gz docker-compose.yml docker-compose.* .env "$PROD_USER@$PROD_SERVER:$PROD_DIR/"
}

tag_version() {
    VERSION=$(date +"%Y.%m.%d-%H%M")
    execute git tag "deploy-${VERSION}"
}

cleanup() {
    log "Cleaning up local files..."
    execute rm -f deploy.tar.gz
}

deploy_to_server() {
    log "Deploying to server..."
    execute ssh $PROD_USER@$PROD_SERVER bash << 'EOF'
        PROD_DIR="/home/ubuntu/docker/dataviz"
        BACKUP_DIR="${PROD_DIR}/backups"
        set -eo pipefail
        cd "${PROD_DIR}"

        # Backup with rotation
        MAX_BACKUPS=5
        mkdir -p "${BACKUP_DIR}"
        backup_file="${BACKUP_DIR}/data-backup-$(date +%Y%m%d_%H%M%S).tar.xz"
        if [ -d "data" ]; then
            tar -cJf "${backup_file}" data/ || {
                echo "Backup failed"
                exit 1
            }
            # Rotate old backups
            ls -t "${BACKUP_DIR}"/data-backup-*.tar.xz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
        fi

        # Load environment
        set -a
        source .env
        set +a

        # Extract and setup
        tar xzf deploy.tar.gz
        sudo chown -R ubuntu:ubuntu data/
        sudo chmod -R 755 data/

        # Docker operations
        export BUILD_DATE=$(date +%Y%m%d_%H%M%S)
        docker compose -f docker-compose.yml down || true
        docker compose -f docker-compose.yml build --no-cache
        docker compose -f docker-compose.yml  up -d

        # Health check with timeout
        TIMEOUT=60
        end=$((SECONDS + TIMEOUT))
        healthy=false
        while [ $SECONDS -lt $end ]; do
            if docker compose ps | grep -q "healthy"; then
                healthy=true
                break
            fi
            sleep 5
        done

        if [ "$healthy" = false ]; then
            echo "Services failed health check after ${TIMEOUT} seconds"
            docker compose logs
            # Consider rolling back here
            exit 1
        fi

        rm -f deploy.tar.gz
EOF
}


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

# Main execution
log "Starting deployment to ${PROD_SERVER}..."
[ "$DRY_RUN" = true ] && log "DRY RUN MODE - No changes will be made"

check_branch
create_deployment_package
copy_files
tag_version
deploy_to_server
cleanup

log "Deployment $([ "$DRY_RUN" = true ] && echo "simulation ")complete!"