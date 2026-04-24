import re
import ollama
from pathlib import Path
from prefect import task, flow
from prefect.artifacts import create_markdown_artifact

from src.schemas.models import ResearchTopic, ResearchRequest, ResearchResult

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

@task(name="perform_research", description="Simulates gathering information on a topic.")
def perform_research(topic: ResearchTopic) -> str:
    """
    Performs research on a given topic using local AI.
    """
    prompt = f"Perform technical research on the following topic: {topic.query}. Depth level requested: {topic.depth}. Provide factual findings in Markdown format."
    
    response = ollama.chat(model='qwen2.5-coder:3b', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
    ])
    
    findings = response['message']['content']
    return f"### Research Findings for: {topic.query}\n\n{findings}\n\n"

class ResearchDepartment:
    """
    Handles the execution of research missions.
    """
    def __init__(self, request: ResearchRequest):
        self.request = request
        self.output_dir = PROJECT_ROOT / "missions" / "research"
        self.output_path = self.output_dir / f"{self.request.mission_id}_research.md"

    def execute(self) -> ResearchResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        aggregated_findings = f"# Research Mission: {self.request.mission_id}\n\n"
        
        for topic in self.request.research_topics:
            findings = perform_research(topic)
            aggregated_findings += findings
            
        # Write report to file
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(aggregated_findings)
            
        # Create Artifact for Prefect UI
        safe_key = re.sub(r'[^a-z0-9\-]', '-', self.request.mission_id.lower())
        create_markdown_artifact(
            key=f"research-report-{safe_key}",
            markdown=aggregated_findings,
            description=f"Findings for {self.request.mission_id}"
        )
        
        return ResearchResult(
            status="success",
            data=aggregated_findings,
            output_path=str(self.output_path)
        )

@flow(name="gather_context", description="Main flow for the Research Department.")
def gather_context(request: ResearchRequest) -> ResearchResult:
    """
    Flow entrypoint for gathering research context.
    """
    department = ResearchDepartment(request)
    return department.execute()

if __name__ == "__main__":
    # Test execution
    test_request = ResearchRequest(
        mission_id="research-01",
        research_topics=[
            ResearchTopic(query="Model Context Protocol", depth="technical"),
            ResearchTopic(query="Multi-Agent Orchestration", depth="standard")
        ]
    )
    result = gather_context(test_request)
    print(f"Research Status: {result.status}")
