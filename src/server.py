from fastmcp import FastMCP
from prefect.deployments import run_deployment
from src.schemas.models import BeatPublishRequest
from src.flows.publishing import publish_beat_pipeline
import asyncio

mcp = FastMCP("ChronoGateway")

@mcp.tool()
async def dispatch_beat_publishing(request: BeatPublishRequest) -> dict:
    """
    Dispatch a beat publishing mission to the Prefect orchestrator.
    This triggers the render and upload pipeline.
    """
    try:
        # Example of triggering deployment in production:
        # run = await run_deployment(
        #     name="publish_beat_pipeline/default", 
        #     parameters={"request": request.model_dump()}
        # )
        # flow_run_url = f"http://localhost:4200/flow-runs/flow-run/{run.id}"
        
        # Triggering the flow directly for local testing/baseline
        result = await publish_beat_pipeline(request)
        
        return {
            "status": "success",
            "message": "Publishing pipeline dispatched successfully",
            "flow_run_url": "http://localhost:4200/flow-runs/flow-run/local-mock-id",
            "result": result.model_dump()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
