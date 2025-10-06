#!/bin/bash

echo "🛑 Stopping Sunchart services..."

# Find and kill gunicorn processes
GUNICORN_PIDS=$(pgrep -f "gunicorn.*api:create_app")
if [ ! -z "$GUNICORN_PIDS" ]; then
    echo "🔹 Stopping backend (gunicorn)..."
    kill $GUNICORN_PIDS
    echo "✅ Backend stopped"
else
    echo "⚠️  No backend process found"
fi

# Find and kill npm serve processes
NPM_PIDS=$(pgrep -f "npm run serve")
if [ ! -z "$NPM_PIDS" ]; then
    echo "🔹 Stopping frontend (npm)..."
    kill $NPM_PIDS
    echo "✅ Frontend stopped"
else
    echo "⚠️  No frontend process found"
fi

# Also kill any node processes related to vue-cli-service
NODE_PIDS=$(pgrep -f "vue-cli-service serve")
if [ ! -z "$NODE_PIDS" ]; then
    echo "🔹 Stopping Vue dev server..."
    kill $NODE_PIDS
    echo "✅ Vue dev server stopped"
fi

echo ""
echo "✅ All services stopped"
