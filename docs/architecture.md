# RescueNet Slack — Architecture

## Overview

RescueNet Slack keeps the existing RescueNet AI backend and wraps it with a Slack-native interface. Slack is the primary disaster-coordination UX and the main submission surface. The Streamlit Command Center is a transparent operational view over the same incident store, evidence, approvals, and audit trail.

## High-Level Flow

```
Slack Workspace
  -> /rescuenet command or @RescueNet mention
  -> slack_app: command parsing, event handling, Block Kit rendering
  -> rescuenet_slack.orchestrator: incident extraction
  -> slack_app.context_search: Slack Real-Time Search (demo adapter)
  -> mcp_server.tools: weather, shelter, hospital, route, resource, audit
  -> backend.services.rescue_graph: LangGraph multi-agent workflow
  -> rescuenet_slack.risk_engine: deterministic 0-100 scoring
  -> rescuenet_slack.response_planner: recommended actions
  -> rescuenet_slack.safety: confidence + human approval gate
  -> rescuenet_slack.store: SQLite persistence
  -> slack_app.blockkit: Block Kit incident card
  -> Human approval in Slack (Approve / Revise / Escalate / View Evidence / Refresh)
  -> Audit trail (SQLite + data/audit_log.jsonl)
```

## Agent Mapping

| Logical Agent | Implementation |
|---|---|
| Incident Detection Agent | `rescuenet_slack/orchestrator.py::extract_incident` |
| Slack Context Intelligence Agent | `slack_app/context_search.py::build_slack_context` |
| Hazard Intelligence Agent | `mcp_server/tools.py::get_weather_alert` |
| Resource Discovery Agent | `mcp_server/tools.py::get_available_resources`, `get_shelter_capacity` |
| Risk & Priority Agent | `rescuenet_slack/risk_engine.py::score_incident` |
| Response Planning Agent | `rescuenet_slack/response_planner.py::build_response_plan` |
| Verification/Safety Agent | `rescuenet_slack/safety.py::review_plan` |
| Incident Commander Agent | `slack_app/actions.py::handle_incident_action` (human-in-the-loop) |
| Multi-Agent Rescue Graph | `backend/services/rescue_graph.py::run_rescue_graph` (LangGraph) |

## Risk Scoring

Deterministic 0–100 score across 7 factors. LLM may explain but never decides the score.

| Factor | Max Points |
|---|---|
| People affected | 20 |
| Vulnerable groups | 15 |
| Medical urgency | 12 |
| Hazard severity | 15 |
| Escalation trend (Slack context) | 10 |
| Access constraints (route risk) | 15 |
| Resource gap | 13 |
| **Total** | **100** |

Priority tiers: LOW (0–29) | MODERATE (30–49) | HIGH (50–69) | SEVERE (70–84) | CRITICAL (85–100)

## Data Layer

SQLite database at `data/rescuenet.db`. Tables:

- `incidents` — extracted incident records with risk score, priority tier, approval status
- `evidence` — Slack context and MCP context snapshots per incident
- `response_plans` — generated action plans per incident
- `approvals` — human approval decisions
- `audit_events` — full audit trail
- `integration_status` — live vs demo adapter status per integration

Both Slack (via FastAPI) and Streamlit read from the same SQLite store.

## MCP Tool Layer

`mcp_server/tools.py` exposes a local facade:

- `get_weather_alert(location)` — weather risk and rainfall data
- `get_shelter_capacity(location)` — shelter names, capacity, available spaces
- `get_available_resources(location)` — rescue boats, ambulances, volunteers, supplies
- `get_hospital_status(location)` — emergency beds, ambulances, trauma readiness
- `get_route_risk(location)` — blocked routes, recommended route
- `log_incident_action(incident_id, action)` — audit logging

Currently uses demo JSON files in `data/`. Replace by pointing `TOOL_REGISTRY` to a real MCP server.

## Slack Real-Time Search Abstraction

`slack_app/context_search.py` provides:

- `search_slack_context(query, channels, time_window)`
- `retrieve_related_incident_threads(location, hazard_type)`
- `retrieve_resource_mentions(location)`
- `retrieve_latest_field_reports(location)`

Currently uses `data/slack_demo_messages.json` (mode: `mock_rts_search`). Replace with Slack Real-Time Search API by adding credentials and updating the search functions.

## Human-in-the-Loop Safety

The agent never dispatches resources automatically. Every incident card requires one of:

- Approve Response Plan → status: `approved`
- Request Revision → status: `revision_requested`
- Escalate to Commander → status: `escalated`

All decisions are written to the audit trail.

## Component Map

```
backend/
  main.py                  FastAPI app, all API endpoints
  services/rescue_graph.py LangGraph multi-agent workflow
  agents/                  10 specialist agents
  a2a/protocol.py          Agent-to-agent message protocol
  database/mongo.py        OperationalDataStore (in-memory + extended city data)

rescuenet_slack/
  orchestrator.py          Incident extraction + full analysis pipeline
  risk_engine.py           Deterministic 0-100 scoring
  response_planner.py      Action plan generation
  safety.py                Confidence + human approval gate
  incident_models.py       Pydantic models + priority tier logic
  store.py                 SQLite persistence layer
  audit_log.py             JSONL audit log writer

slack_app/
  app.py                   Slack Bolt app, App Home, all handlers
  commands.py              /rescuenet command router (7 commands)
  events.py                @mention handler
  actions.py               Button action handler
  blockkit.py              Block Kit card builder
  context_search.py        Slack Real-Time Search abstraction
  config.py                Slack settings from environment

mcp_server/
  tools.py                 MCP-compatible tool facade
  server.py                Standalone MCP FastAPI app
  schemas.py               Pydantic schemas for tool outputs

command_center/
  streamlit_app.py         Streamlit operational command center (5 tabs)

data/
  slack_demo_messages.json Demo Slack messages for context search
  shelters_demo.json       Demo shelter data
  resources_demo.json      Demo resource data
  weather_demo.json        Demo weather data
  audit_log.jsonl          JSONL audit log
  rescuenet.db             SQLite incident store (auto-created)
```
