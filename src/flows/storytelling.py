import re
import ollama
from pathlib import Path
from prefect import task, flow
from prefect.artifacts import create_markdown_artifact

from src.schemas.models import StoryTopic, MissionRequest, MissionResult

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

@task(name="generate_draft", description="Generates a story draft for a specific topic.")
def generate_draft(topic: StoryTopic) -> str:
    """
    Generates content for a given story topic using local AI.
    """
    prompt = f"Write a professional story draft about {topic.topic_name} specifically for {topic.target_audience}. Use Markdown formatting."
    
    response = ollama.chat(model='qwen2.5-coder:3b', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    
    content = response['message']['content']
    return f"## Topic: {topic.topic_name}\n\n{content}\n\n"

class StorytellingFlow:
    """
    Object-oriented handler for the storytelling process.
    """
    def __init__(self, request: MissionRequest):
        self.request = request
        self.output_dir = PROJECT_ROOT / "missions"
        self.output_path = self.output_dir / f"{self.request.mission_id}.md"

    def execute(self) -> MissionResult:
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        aggregated_content = f"# Mission Report: {self.request.mission_id}\n\n"
        
        # Process each topic via the Prefect task
        for topic in self.request.topics:
            draft = generate_draft(topic)
            aggregated_content += draft
            
        # Write output to the file system
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(aggregated_content)
            
        # Sanitize mission_id for artifact key (only lowercase, numbers, dashes)
        safe_key = re.sub(r'[^a-z0-9\-]', '-', self.request.mission_id.lower())
        
        # Publish artifact to Prefect UI
        create_markdown_artifact(
            key=f"mission-report-{safe_key}",
            markdown=aggregated_content,
            description=f"Chronicle for {self.request.mission_id}"
        )
        
        return MissionResult(
            status="success",
            output_path=str(self.output_path)
        )

@flow(name="write_chronicle", description="Main flow to write a chronicle from a mission request.")
def write_chronicle(request: MissionRequest) -> MissionResult:
    """
    Flow entrypoint that loops through topics, writes the chronicle, and returns a MissionResult.
    """
    storytelling = StorytellingFlow(request)
    return storytelling.execute()

if __name__ == "__main__":
    import sys
    # Only run the manual test if no arguments are passed (i.e. not being called for a deployment)
    if len(sys.argv) == 1:
        # Test execution
        test_request = MissionRequest(
            mission_id="mission-alpha-01",
            topics=[
                StoryTopic(topic_name="Enterprise AI Integration", target_audience="Enterprise Architects"),
                StoryTopic(topic_name="Agentic Workflows", target_audience="Product Managers")
            ]
        )
        result = write_chronicle(test_request)
        print(f"Mission Result: {result.status} | Output saved to: {result.output_path}")
