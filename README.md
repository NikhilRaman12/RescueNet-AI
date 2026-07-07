# RescueNet Slack

Autonomous Crisis Operations Agent for Slack

Track: Slack Agent for Good

RescueNet Slack upgrades the existing RescueNet AI disaster response system into a Slack-native crisis operations agent. It helps incident commanders, NGOs, field teams, logistics coordinators, shelter operators, medical teams, and volunteers turn fragmented Slack updates into verified, prioritized response plans.

The project preserves the existing RescueNet AI backend, multi-agent rescue graph, MCP-style operational tools, A2A trace output, dashboard assets, and tests. Slack is added as the primary command interface for hackathon demos.

Primary UX: Slack App / Slack Agent

Secondary deployed link: Streamlit Command Center

Deployment targets: Hugging Face Spaces or Streamlit Community Cloud

## Problem

During floods, cyclones, earthquakes, and other emergencies, crucial updates are scattered across Slack channels, field reports, shelter notes, weather alerts, and resource messages. Teams lose time searching for context, validating resource availability, and deciding which incident needs action first.

## Impact

RescueNet Slack gives response teams a shared operational loop:

1. A field report appears in Slack.
2. The agent detects the incident and extracts location, hazard, people at risk, vulnerable groups, and urgency.
3. Slack context search retrieves related reports, resource mentions, blocked roads, shelter updates, and medical notes.
4. MCP-style tools check weather, shelters, hospitals, resources, route risk, and audit logging.
5. The existing RescueNet multi-agent graph scores and enriches the incident.
6. A Slack Block Kit incident card is posted with recommended actions.
7. A human approves, requests revision, or escalates to the commander.
8. The action is logged in an audit trail.

## Slack Features

- Slash command: `/rescuenet`
- Mention handler: `@RescueNet`
- Demo command: `/rescuenet demo`
- Incident analysis command: `/rescuenet analyze "Flood water crossed bridge near Village A. 70 people stranded, elderly and children present."`
- Resource lookup command: `/rescuenet resources Village A`
- Slack Block Kit incident cards
- Interactive buttons:
  - Approve Response Plan
  - Request Revision
  - Escalate to Commander
- Thread-ready response payloads
- Local demo mode without paid APIs

## Secondary Command Center

The Streamlit Command Center is a secondary deployed demo for judges who need a public link. It uses the same `rescuenet_slack` orchestration as the Slack slash command flow and is deployable to Hugging Face Spaces or Streamlit Community Cloud.

Run locally:

```bash
streamlit run streamlit_app.py
```

## Architecture

```text
Slack Workspace
  ->
Slack Agent Interface
  ->
Real-Time Search / Context Retrieval
  ->
RescueNet Multi-Agent Orchestrator
  ->
MCP Tool Layer
  ->
Risk Scoring + Response Planning
  ->
Safety Verification
  ->
Human Approval in Slack
  ->
Audit Trail
```

## Tech Stack

- Python
- FastAPI
- Slack Bolt for Python
- Streamlit
- Pydantic
- LangGraph with sequential fallback
- MCP-compatible local tool facade
- Local Slack Real-Time Search abstraction with demo JSON fallback
- Docker and Docker Compose

## Slack AI, MCP, and Real-Time Search Usage

- Slack AI interface: Slack slash command, mention handler, Block Kit response card, and interactive actions.
- MCP integration: `mcp_server/tools.py` exposes replaceable tools such as `get_weather_alert`, `get_shelter_capacity`, `get_available_resources`, `get_hospital_status`, `get_route_risk`, and `log_incident_action`.
- Real-Time Search abstraction: `slack_app/context_search.py` provides `search_slack_context`, `retrieve_related_incident_threads`, `retrieve_resource_mentions`, and `retrieve_latest_field_reports`. Local demo mode uses `data/slack_demo_messages.json`.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

Open:

- API health: `http://127.0.0.1:8010/health`
- API docs: `http://127.0.0.1:8010/docs`
- Slack agent status: `http://127.0.0.1:8010/api/slack/status`

## Demo Commands

Analyze a field report:

```bash
curl -X POST "http://127.0.0.1:8010/api/slack/analyze" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"Flood water crossed bridge near Village A. 70 people stranded, elderly and children present.\",\"channel\":\"field-reports\",\"user_id\":\"U-demo\"}"
```

Run the Slack demo command locally:

```bash
curl -X POST "http://127.0.0.1:8010/api/slack/command" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"demo\",\"channel\":\"incident-command\",\"user_id\":\"U-demo\"}"
```

Approve a response plan after copying an `incident_id` from the previous response:

```bash
curl -X POST "http://127.0.0.1:8010/api/slack/actions" ^
  -H "Content-Type: application/json" ^
  -d "{\"action_id\":\"approve_response_plan\",\"incident_id\":\"incident-demo\",\"user_id\":\"U-commander\"}"
```

## Environment Variables

```text
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
SLACK_SIGNING_SECRET=
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
OPENAI_API_KEY=
GEMINI_API_KEY=
RESCUENET_LLM_MODEL=
USE_MOCK_SLACK_SEARCH=true
USE_MOCK_MCP_TOOLS=true
APP_ENV=development
USE_LIVE_APIS=true
ENABLE_GUARDRAILS=true
API_HOST=0.0.0.0
API_PORT=8010
```

No secrets are committed. Demo mode works with empty Slack and LLM credentials.

## Docker

```bash
docker compose up --build
```

The backend runs on `http://127.0.0.1:8010`.

## Streamlit Deployment

Use `streamlit_app.py` as the app entrypoint.

- Hugging Face Spaces: SDK `Streamlit`, app file `streamlit_app.py`
- Streamlit Community Cloud: main file path `streamlit_app.py`

Deployment guides:

- `deployment/huggingface_spaces.md`
- `deployment/streamlit_cloud.md`

## Safety

RescueNet Slack is decision support only. It does not replace emergency authorities, dispatch systems, or trained incident commanders. The agent always displays confidence, sources, and a human approval requirement before dispatch or escalation. If confidence is low or resource availability is uncertain, the response plan asks for verification before action.

## Repository Map

- `backend/`: existing RescueNet AI FastAPI backend, rescue graph, agents, MCP service, A2A protocol, and operational APIs.
- `rescuenet_slack/`: Slack-native incident extraction, risk scoring, planning, safety review, audit logging, and orchestration.
- `slack_app/`: Slack command, event, action, Block Kit, client, and context search modules.
- `mcp_server/`: local MCP-compatible tool facade designed to be replaced by a real MCP server.
- `data/`: demo Slack messages, shelter data, resource data, weather data, and generated audit log.
- `docs/`: hackathon architecture, setup, demo, and submission notes.
- `deployment/`: Hugging Face Spaces, Streamlit Community Cloud, Render, and Cloud Run guides.
- `command_center/`: secondary Streamlit Command Center.

## Verification

```bash
python -m pytest
```

The test suite covers the existing RescueNet health/rescue paths and the new Slack status, incident analysis, Block Kit card, command, and action flow.
