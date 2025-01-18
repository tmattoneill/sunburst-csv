#!/bin/bash
set -e

# Configuration
PROD_SERVER="moneill.net"
PROD_USER="ubuntu"
PROD_DIR="/home/ubuntu/docker/dataviz"

echo "Deploying to production..."

# 1. Build local production version
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 2. Create deployment package
git archive --format=tar.gz -o deploy.tar.gz HEAD

# 3. Copy to production server
scp deploy.tar.gz $PROD_USER@$PROD_SERVER:$PROD_DIR/
scp docker-compose.yml docker-compose.prod.yml .env.prod $PROD_USER@$PROD_SERVER:$PROD_DIR/

# 4. SSH into server and deploy
# Add after the tar extract
ssh $PROD_USER@$PROD_SERVER << 'ENDSSH'
cd $PROD_DIR
tar xzf deploy.tar.gz
# Set correct permissions
chown -R sunburst:sunburst data/
chmod -R 755 data/
# Continue with docker commands...
ENDSSH

echo "Deployment complete!"