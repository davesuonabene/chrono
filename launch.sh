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

# 2. Configure Prefect for Maximum SQLite Stability
# Increase timeout to 60s and disable thread checking for async compatibility
export PREFECT_API_DATABASE_CONNECTION_URL="sqlite+aiosqlite:///${HOME}/.prefect/prefect.db?check_same_thread=False&timeout=60"

echo "🚀 Launching Chrono Enterprise AI Orchestrator..."

# 3. Start Prefect Server (Wait longer for it to be fully ready)
echo "📡 Starting Prefect Server..."
prefect server start &
PREFECT_SERVER_PID=$!
sleep 12 

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
