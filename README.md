# Chrono: Enterprise AI Orchestrator

Chrono is a robust, strictly typed AI orchestration system designed for high-reliability content generation and task management. It leverages a "Systems Architect" model where the AI agent (Selene) delegates work to a background factory floor (Prefect) via a Model Context Protocol (MCP) gateway.

## 🏗️ Architecture Overview

The system is divided into three distinct layers:

1.  **The Architect (Selene):** An OpenClaw agent that interprets high-level user requests, validates them against strict Pydantic schemas, and dispatches them as missions.
2.  **The Gateway (FastMCP):** A high-performance bridge (`src/server.py`) that provides tools for the agent to communicate with the orchestration layer.
3.  **The Orchestrator (Prefect):** A background engine (`src/flows/storytelling.py`) that manages the execution lifecycle, retries, and artifact generation.

---

## 📋 Requisites

To run Chrono on any operating system (Linux, macOS, or Windows), you need:

-   **Python 3.10+**
-   **Prefect 3.0+** (Orchestration server and worker)
-   **Pydantic** (Data validation)
-   **FastMCP** (MCP tool server)
-   **OpenClaw** (Agent framework)

---

## 🚀 Setup & Installation

### 1. Initialize Environment
Run the setup script (Linux/macOS) or follow the steps manually:

```bash
# Using the setup script
chmod +x setup_and_test.sh
./setup_and_test.sh
```

**Manual Installation (Universal):**
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install prefect pydantic fastmcp
mkdir -p src/schemas src/flows src/tools inbox processing completed missions
```

### 2. Start Services
You need three background processes running:

1.  **Prefect Server:** `prefect server start` (Dashboard: http://127.0.0.1:4200)
2.  **Prefect Worker:** `prefect worker start --pool workpool`
3.  **Chrono Controller (MCP):** `python src/server.py`

---

## 🛠️ Usage & Workflow

Chrono uses a file-based "Inbox" workflow for maximum controllability:

1.  **Task Assignment:** Drop a mission request (text, JSON, or MD) into the `inbox/` directory.
    *   *Example:* Create `inbox/mission-01.txt` with "Write a report on AI safety for researchers."
2.  **Autonomous Dispatch:** Selene (the agent) detects the file, validates the schema, and moves the task to `processing/`.
3.  **Execution:** Prefect picks up the mission, runs the `write_chronicle` flow, and generates a beautiful **Markdown Artifact** in the dashboard.
4.  **Completion:** Once the output is saved to `missions/`, Selene archives the task in `completed/` and logs the success in `MISSION_LOG.md`.

---

## 💻 Coding & Development

### Directory Structure
-   `src/schemas/models.py`: All data structures MUST be strictly typed Pydantic models.
-   `src/flows/`: Prefect `@flow` and `@task` definitions for specific departments.
-   `src/tools/`: Custom logic for MCP tools.
-   `missions/`: Final production outputs.

### Development Guidelines
-   **Object-Oriented Flows:** Keep flows modular by wrapping logic in classes (see `StorytellingFlow`).
-   **Strict Schema Mapping:** Tools in `server.py` must accept Pydantic models directly to ensure the agent cannot pass malformed data.
-   **Cross-Platform Paths:** Always use Python's `pathlib` for file operations to ensure compatibility between Linux and Windows.

---

## 📝 Monitoring

-   **Prefect Dashboard:** [http://127.0.0.1:4200](http://127.0.0.1:4200) - View flow runs, logs, and artifacts.
-   **Mission Log:** Check `MISSION_LOG.md` for a quick ledger of all historical activity.
