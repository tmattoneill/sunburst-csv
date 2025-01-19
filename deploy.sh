#!/bin/bash
set -e

# Configuration
PROD_SERVER="moneill.net"
PROD_USER="ubuntu"
PROD_DIR="/home/ubuntu/docker/dataviz"

echo "Deploying to production..."

# 1. Create deployment package
git archive --format=tar.gz -o deploy.tar.gz HEAD

# 2. Copy configuration files
echo "Copying configuration files..."
scp deploy.tar.gz docker-compose.yml docker-compose.prod.yml .env.prod nginx.conf $PROD_USER@$PROD_SERVER:$PROD_DIR/

# 3. SSH into server and deploy
ssh $PROD_USER@$PROD_SERVER << 'ENDSSH'
cd $PROD_DIR

# Backup existing data
if [ -d "data" ]; then
    echo "Backing up existing data..."
    tar -czf data-backup-$(date +%Y%m%d_%H%M%S).tar.gz data/
fi

# Extract new code
echo "Extracting deployment package..."
tar xzf deploy.tar.gz

# Set correct permissions
echo "Setting permissions..."
sudo chown -R sunburst:sunburst data/
sudo chmod -R 755 data/

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Build and start new containers
echo "Building and starting containers..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Clean up
echo "Cleaning up..."
rm deploy.tar.gz
ENDSSH

echo "Deployment complete!"