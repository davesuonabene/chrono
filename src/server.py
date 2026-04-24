import json
import os
from pathlib import Path
from fastmcp import FastMCP
from prefect.deployments import run_deployment

from src.schemas.models import MissionRequest, ResearchRequest

mcp = FastMCP("Chrono_Controller")
PROJECT_ROOT = Path(__file__).resolve().parent.parent

@mcp.tool()
def dispatch_story_mission(request: MissionRequest) -> str:
    """
    Dispatch a storytelling mission to the Prefect orchestrator.
    """
    flow_run = run_deployment(
        name="write_chronicle/chrono-story-v1",
        parameters={"request": request.model_dump()}
    )
    
    prefect_ui_url = os.getenv("PREFECT_UI_URL", "http://127.0.0.1:4200")
    flow_run_url = f"{prefect_ui_url}/flow-runs/flow-run/{flow_run.id}"
    expected_output_path = str(PROJECT_ROOT / "missions" / f"{request.mission_id}.md")
    
    return json.dumps({
        "status": "Storytelling mission dispatched",
        "flow_run_url": flow_run_url,
        "expected_output_path": expected_output_path
    })

@mcp.tool()
def dispatch_research_mission(request: ResearchRequest) -> str:
    """
    Dispatch a research mission to gather context before writing.
    """
    # Trigger the research flow
    flow_run = run_deployment(
        name="gather_context/chrono-research-v1",
        parameters={"request": request.model_dump()}
    )
    
    prefect_ui_url = os.getenv("PREFECT_UI_URL", "http://127.0.0.1:4200")
    flow_run_url = f"{prefect_ui_url}/flow-runs/flow-run/{flow_run.id}"
    expected_output_path = str(PROJECT_ROOT / "missions" / "research" / f"{request.mission_id}_research.md")
    
    return json.dumps({
        "status": "Research mission dispatched",
        "flow_run_url": flow_run_url,
        "expected_output_path": expected_output_path
    })

if __name__ == "__main__":
    mcp.run()
