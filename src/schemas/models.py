from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

# --- STORYTELLING DEPARTMENT ---

class StoryTopic(BaseModel):
    topic_name: str
    target_audience: str

class MissionRequest(BaseModel):
    mission_id: str
    topics: List[StoryTopic]

class MissionResult(BaseModel):
    status: str
    output_path: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- RESEARCH DEPARTMENT ---

class ResearchTopic(BaseModel):
    query: str
    depth: str = "standard"  # e.g., "standard", "deep", "technical"

class ResearchRequest(BaseModel):
    mission_id: str
    research_topics: List[ResearchTopic]

class ResearchResult(BaseModel):
    status: str
    data: str  # The aggregated findings
    output_path: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

if __name__ == "__main__":
    # Test the new Research structures
    topic = ResearchTopic(query="Prefect 3.0 SQLite locking", depth="deep")
    request = ResearchRequest(mission_id="res-001", research_topics=[topic])
    print("Research Models Validated!")
    print(request.model_dump_json(indent=2))
