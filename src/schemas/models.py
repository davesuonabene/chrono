from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

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

if __name__ == "__main__":
    # Quick test to ensure everything is strictly typed and works
    topic = StoryTopic(topic_name="Enterprise AI", target_audience="CTOs")
    request = MissionRequest(mission_id="m-001", topics=[topic])
    result = MissionResult(status="success", output_path="/tmp/output.json")
    
    print("Test successful!")
    print(request.model_dump_json(indent=2))
    print(result.model_dump_json(indent=2))
