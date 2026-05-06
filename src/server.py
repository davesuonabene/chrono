from fastmcp import FastMCP
from prefect.deployments import run_deployment
from src.schemas.models import BeatPublishRequest, BeatPreparationResult
from src.flows.publishing import publish_beat_pipeline
import asyncio
import httpx
import os

mcp = FastMCP("ChronoGateway")

BEAT_MANAGER_API_URL = os.getenv("BEAT_MANAGER_API_URL", "http://localhost:8000")

@mcp.tool()
async def search_available_beats(collection: str = None) -> str:
    """
    Query the BeatManager Library API for unassigned beats ready for publishing.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Query param collection could be used if API supports it, using unassigned_only for now
            response = await client.get(f"{BEAT_MANAGER_API_URL}/library/beats?unassigned_only=true")
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"{{\"error\": \"{str(e)}\"}}"

@mcp.tool()
async def search_cover_art() -> str:
    """
    Query the BeatManager Library API to retrieve available image assets for cover art.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BEAT_MANAGER_API_URL}/library/images")
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"{{\"error\": \"{str(e)}\"}}"

@mcp.tool()
async def link_and_prepare_beat(beat_id: str, image_id: str) -> str:
    """
    Links a cover image to a beat via BeatManager API and retrieves the absolute paths 
    formatted as a BeatPublishRequest payload, ready for the dispatch_beat_publishing tool.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 1. Link the image to the beat
            link_res = await client.post(
                f"{BEAT_MANAGER_API_URL}/library/beats/{beat_id}/link",
                json={"image_id": image_id}
            )
            link_res.raise_for_status()

            # 2. Get the updated payload
            payload_res = await client.get(f"{BEAT_MANAGER_API_URL}/library/beats/{beat_id}/payload")
            payload_res.raise_for_status()
            
            # The API returns a BeatPreparationResult
            result = BeatPreparationResult(**payload_res.json())
            
            if not result.is_ready_for_dispatch:
                return "{\"error\": \"Beat is not fully prepared for dispatch (missing paths).\"}"

            # 3. Formulate the valid BeatPublishRequest JSON string
            publish_request = BeatPublishRequest(
                audio_path=result.audio_path,
                image_path=result.image_path,
                title=result.suggested_title or "Untitled Beat",
                description="Automatically published via Chrono.",
                tags=["beat", "instrumental"]
            )
            return publish_request.model_dump_json()

        except Exception as e:
            return f"{{\"error\": \"{str(e)}\"}}"

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
    # Run the MCP server using SSE transport to keep it alive in the background
    mcp.run(transport="sse", port=8001)
