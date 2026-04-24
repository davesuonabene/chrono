#!/bin/bash
# setup_and_test.sh

set -e

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements quietly
pip install --quiet --upgrade pip
pip install --quiet fastmcp prefect pydantic

# Create directories
mkdir -p src/schemas src/flows src/tools missions

echo "Setup completed successfully."

# Start the Prefect server in the background
prefect server start &
PREFECT_PID=$!

# Wait a few seconds for the server to spin up
sleep 10

# Build and apply the deployments
prefect deploy src/flows/storytelling.py:write_chronicle -n chrono-story-v1
prefect deploy src/flows/research.py:gather_context -n chrono-research-v1

# Execute a dry-run test using the Prefect CLI
prefect deployment run write_chronicle/chrono-story-v1 --params '{"request": {"mission_id": "dry-run-001", "topics": [{"topic_name": "Prefect Orchestration", "target_audience": "Engineers"}]}}'

echo ""
echo "=========================================================="
echo " SUCCESS! The deployment was applied and dry-run started."
echo " The Prefect dashboard is available at: http://127.0.0.1:4200"
echo "=========================================================="
