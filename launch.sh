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
    echo "🏗️ Creating and starting new chrono-postgres container with persistent volume..."
    docker run --name chrono-postgres \
      -e POSTGRES_USER=postgres \
      -e POSTGRES_PASSWORD=postgres \
      -e POSTGRES_DB=prefect \
      -v chrono_postgres_data:/var/lib/postgresql \
      -p 5432:5432 \
      -d postgres
fi

# 3. Configure Prefect Database Connection
export PREFECT_API_DATABASE_CONNECTION_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/prefect"

# 4. Wait for Database to be Ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker exec chrono-postgres pg_isready -U postgres -d prefect >/dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    fi
    echo "waiting... ($i/30)"
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ Error: Database did not become ready in time."
        exit 1
    fi
done

echo "🚀 Launching Chrono Enterprise AI Orchestrator..."

# 5. Start Prefect Server
echo "📡 Starting Prefect Server..."
prefect server start &
PREFECT_SERVER_PID=$!
sleep 15 

# 6. Start Prefect Worker
echo "👷 Starting Prefect Worker (pool: workpool)..."
prefect worker start --pool workpool &
PREFECT_WORKER_PID=$!
sleep 3

# 7. Start FastMCP Chrono Controller
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
