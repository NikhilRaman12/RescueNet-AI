# RescueNet Slack Architecture

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

The existing RescueNet AI backend remains the core emergency reasoning engine. Slack-native modules wrap the rescue graph with command parsing, context retrieval, MCP-compatible tool calls, response planning, Block Kit rendering, and human approval.

Slack is the primary UX. The Streamlit Command Center is a secondary deployed demo that calls the same orchestration for public judging links.

## Components

- `backend/main.py`: FastAPI API, existing RescueNet endpoints, and local Slack demo endpoints.
- `backend/services/rescue_graph.py`: existing multi-agent rescue workflow.
- `slack_app/`: Slack slash command, mention, action, Block Kit, context search, and posting helpers.
- `rescuenet_slack/`: incident extraction, risk scoring, response planning, safety review, audit trail, and orchestration.
- `mcp_server/`: local MCP-compatible tool facade.
- `data/`: deterministic demo data for Slack search, weather, shelters, resources, and audit logs.
- `command_center/`: Streamlit secondary command center for Hugging Face Spaces or Streamlit Community Cloud.

## Data Flow

1. A Slack command or mention enters `slack_app`.
2. `rescuenet_slack.orchestrator` extracts the incident.
3. `slack_app.context_search` retrieves related Slack context.
4. `mcp_server.tools` gathers weather, shelter, hospital, route, resource, and audit context.
5. `backend.services.rescue_graph.run_rescue_graph` runs the existing RescueNet agent sequence.
6. `rescuenet_slack.risk_engine` computes severity.
7. `rescuenet_slack.response_planner` creates recommended actions.
8. `rescuenet_slack.safety` adds confidence, source, and human approval controls.
9. `slack_app.blockkit` renders the incident card.
10. Button actions write to SQLite approvals/audit tables and `data/audit_log.jsonl`.
