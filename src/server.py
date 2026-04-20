import json
import os
from pathlib import Path
from fastmcp import FastMCP
from prefect.deployments import run_deployment

from src.schemas.models import MissionRequest

mcp = FastMCP("Chrono_Controller")
PROJECT_ROOT = Path(__file__).resolve().parent.parent

@mcp.tool()
def dispatch_story_mission(request: MissionRequest) -> str:
    """
    Dispatch a storytelling mission to the Prefect orchestrator.
    """
    # Trigger the write-chronicle flow passing the validated Pydantic dictionary
    flow_run = run_deployment(
        name="write_chronicle/default",
        parameters={"request": request.model_dump()}
    )
    
    # Construct the Prefect Flow Run URL
    prefect_ui_url = os.getenv("PREFECT_UI_URL", "http://127.0.0.1:4200")
    flow_run_url = f"{prefect_ui_url}/flow-runs/flow-run/{flow_run.id}"
    
    # Define the expected output path
    expected_output_path = str(PROJECT_ROOT / "missions" / f"{request.mission_id}.md")
    
    return json.dumps({
        "flow_run_url": flow_run_url,
        "expected_output_path": expected_output_path
    })

if __name__ == "__main__":
    mcp.run()
