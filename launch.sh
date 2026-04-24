#!/bin/bash

# Chrono: Enterprise AI Orchestrator - Super-Robust Launch Script

# Navigate to the project root
cd "$(dirname "$0")"

echo "=========================================================="
echo "🧹 Cleaning up existing Chrono & Prefect processes..."
ps aux | grep -E "prefect|server.py" | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>/dev/null
echo "=========================================================="

# 1. Activate Virtual Environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment (venv) not found."
    exit 1
fi

# 2. Ensure PostgreSQL Container is Running
echo "🐘 Checking PostgreSQL container (chrono-postgres)..."
if [ "$(docker ps -aq -f name=chrono-postgres)" ]; then
    if [ ! "$(docker ps -q -f name=chrono-postgres)" ]; then
        echo "🔄 Starting existing chrono-postgres container..."
        docker start chrono-postgres
    else
        echo "✅ chrono-postgres is already running."
    fi
else
    echo "🏗️ Creating and starting new chrono-postgres container..."
    docker run --name chrono-postgres \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=prefect \
      -p 5432:5432 \
      -d postgres
fi

# 3. Configure Prefect Database Connection
export PREFECT_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/prefect"

echo "🚀 Launching Chrono Enterprise AI Orchestrator..."

# 4. Start Prefect Server (Wait longer for it to be fully ready)
echo "📡 Starting Prefect Server..."
prefect server start &
PREFECT_SERVER_PID=$!
sleep 15 

# 4. Start Prefect Worker
echo "👷 Starting Prefect Worker (pool: workpool)..."
prefect worker start --pool workpool &
PREFECT_WORKER_PID=$!
sleep 3

# 5. Start FastMCP Chrono Controller
echo "🏗️  Starting FastMCP Chrono Controller..."
export PYTHONPATH=$PYTHONPATH:.
python src/server.py &
CHRONO_CONTROLLER_PID=$!
sleep 2

echo "=========================================================="
echo "✅ All systems are online!"
echo "----------------------------------------------------------"
echo "📊 Dashboard: http://127.0.0.1:4200"
echo "=========================================================="
echo "PIDs: Server:$PREFECT_SERVER_PID | Worker:$PREFECT_WORKER_PID | Controller:$CHRONO_CONTROLLER_PID"
