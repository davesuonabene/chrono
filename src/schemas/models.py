from pydantic import BaseModel, Field
from typing import Optional, List

class BeatPublishRequest(BaseModel):
    audio_path: str = Field(..., description="Path to the audio file")
    image_path: str = Field(..., description="Path to the background image")
    title: str = Field(..., description="Title of the beat/video")
    description: Optional[str] = Field("", description="Description for YouTube")
    tags: List[str] = Field(default_factory=list, description="YouTube tags")

class TaskResult(BaseModel):
    """Base generic task result to satisfy strict type constraints"""
    success: bool
    error_message: Optional[str] = None

class RenderTaskResult(TaskResult):
    video_path: Optional[str] = None

class UploadTaskResult(TaskResult):
    youtube_id: Optional[str] = None

class PublishingResult(BaseModel):
    status: str = Field(..., description="Overall status of the publishing pipeline")
    video_path: Optional[str] = Field(None, description="Path to the rendered video")
    youtube_id: Optional[str] = Field(None, description="YouTube video ID if published successfully")
    error_message: Optional[str] = Field(None, description="Error message if failed")
