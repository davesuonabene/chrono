import os
import httpx
from prefect import flow, task, get_run_logger
from src.schemas.models import (
    BeatPublishRequest, 
    PublishingResult, 
    RenderTaskResult, 
    UploadTaskResult
)

# BEAT_MANAGER_API_URL should be set in the environment or Prefect blocks
BEAT_MANAGER_API_URL = os.getenv("BEAT_MANAGER_API_URL", "http://localhost:8000")

@task(name="Render Beat Video", retries=1, retry_delay_seconds=30, timeout_seconds=3600)
async def render_beat_video(request: BeatPublishRequest) -> RenderTaskResult:
    logger = get_run_logger()
    logger.info(f"Requesting render for {request.title}")
    
    async with httpx.AsyncClient(timeout=3600.0) as client:
        try:
            response = await client.post(
                f"{BEAT_MANAGER_API_URL}/publish/render",
                json={
                    "audio_path": request.audio_path,
                    "image_path": request.image_path,
                    "title": request.title
                }
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Render completed. Video path: {data['video_path']}")
            return RenderTaskResult(success=True, video_path=data["video_path"])
        except Exception as e:
            logger.error(f"Render failed: {e}")
            return RenderTaskResult(success=False, error_message=str(e))

@task(name="Upload Video to YouTube", retries=3, retry_delay_seconds=60, timeout_seconds=1800)
async def upload_to_youtube(video_path: str, request: BeatPublishRequest) -> UploadTaskResult:
    logger = get_run_logger()
    logger.info(f"Requesting upload for video at {video_path}")
    
    async with httpx.AsyncClient(timeout=1800.0) as client:
        try:
            response = await client.post(
                f"{BEAT_MANAGER_API_URL}/publish/upload",
                json={
                    "video_path": video_path,
                    "title": request.title,
                    "description": request.description,
                    "tags": request.tags
                }
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Upload completed. YouTube ID: {data['youtube_id']}")
            return UploadTaskResult(success=True, youtube_id=data["youtube_id"])
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            return UploadTaskResult(success=False, error_message=str(e))

class BeatPublishingDepartment:
    """
    Object-oriented wrapper for the publishing workflow.
    Adheres to SOLID principles by decoupling the orchestrator from the actual rendering/uploading logic.
    """
    def __init__(self, request: BeatPublishRequest):
        self.request = request
        self.logger = get_run_logger()
        
    async def process(self) -> PublishingResult:
        self.logger.info(f"Starting BeatPublishingDepartment process for '{self.request.title}'")
        
        # 1. Rendering Phase
        render_result: RenderTaskResult = await render_beat_video(self.request)
        if not render_result.success or not render_result.video_path:
            return PublishingResult(
                status="failed", 
                error_message=f"Rendering failed: {render_result.error_message}"
            )
            
        # 2. Upload Phase
        upload_result: UploadTaskResult = await upload_to_youtube(render_result.video_path, self.request)
        if not upload_result.success or not upload_result.youtube_id:
            return PublishingResult(
                status="failed", 
                video_path=render_result.video_path,
                error_message=f"Upload failed: {upload_result.error_message}"
            )
            
        return PublishingResult(
            status="success",
            video_path=render_result.video_path,
            youtube_id=upload_result.youtube_id
        )

@flow(name="publish_beat_pipeline", description="Orchestrates the rendering and publishing of beats via BeatManager")
async def publish_beat_pipeline(request: BeatPublishRequest) -> PublishingResult:
    department = BeatPublishingDepartment(request)
    return await department.process()
