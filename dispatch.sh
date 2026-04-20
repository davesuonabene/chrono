#!/bin/bash
set -e
cd /home/dave/.openclaw/workspace
source projects/chrono/venv/bin/activate
export PREFECT_HOME="$(pwd)/projects/chrono/.prefect"
export PREFECT_API_URL="http://127.0.0.1:4200/api"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/projects/chrono"

# Start server if not running
if ! curl -s http://127.0.0.1:4200/api/health > /dev/null; then
    prefect server start --background
    sleep 10
fi

# Run directly using the flow function (no deployment needed for local execution)
python3 -c '
import json
import sys
import os
from src.flows.storytelling import write_chronicle
from src.schemas.models import MissionRequest, StoryTopic

# Read task from file or env
mission_id = "task01"
# For now hardcoding or we could read the inbox file again
topic_name = "a lonely stupid guy"
target_audience = "fans of comedy"

request = MissionRequest(
    mission_id=mission_id,
    topics=[StoryTopic(topic_name=topic_name, target_audience=target_audience)]
)

try:
    result = write_chronicle(request)
    print(json.dumps({"status": result.status, "output_path": result.output_path}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
'
