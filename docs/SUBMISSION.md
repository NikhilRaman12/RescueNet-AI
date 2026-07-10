# Devpost Submission - RescueNet Slack

## Project Name

RescueNet Slack

## Tagline

Slack-native crisis operations agent that turns scattered disaster updates into verified, prioritized, human-approved response plans.

## Track

Slack Agent for Good

## Public Links

- Public GitHub URL: `[add public GitHub repository URL]`
- Slack developer sandbox URL: `[add Slack sandbox invite or workspace URL after owner grants access]`
- Slack backend URL: `[add deployed backend URL]`
- Streamlit deployed URL: `[add Streamlit Community Cloud or Hugging Face Spaces URL]`
- Demo video URL: `[add 3-minute demo video URL]`

## Brief Description

RescueNet Slack is submitted as a Slack-native disaster-coordination agent, not as a Streamlit disaster dashboard. NGOs, field volunteers, and incident commanders coordinate response from Slack through `/rescuenet demo`, `/rescuenet analyze <text>`, the Report Incident modal, or an `@RescueNet` mention. The agent extracts incident details, retrieves Slack context, gathers MCP evidence, scores risk deterministically, generates a response plan, verifies safety constraints, and posts a Block Kit incident card that requires human approval before any operational plan is marked approved.

## Impact Statement

During floods, cyclones, earthquakes, and similar emergencies, response updates often arrive across multiple Slack channels. RescueNet Slack reduces context-search time, makes prioritization auditable, and keeps humans in control before resource commitments. It is decision support only and does not replace emergency authorities or dispatch real resources autonomously.

## Inspiration

The project was inspired by disaster-response teams that already coordinate in messaging platforms but lack a shared, evidence-backed operational view. Slack is where responders are already communicating, so RescueNet brings triage, evidence, planning, and approval directly into that workflow.

## Problem

Critical incident reports, shelter capacity notes, weather alerts, resource availability, and medical updates are scattered across channels. Commanders can miss evidence, over-trust unverified reports, or approve plans without a durable audit trail.

## What It Does

- Accepts field reports through Slack slash commands, mentions, and the Report Incident shortcut modal.
- Shows an App Home with recent incidents and command shortcuts.
- Searches demo Slack context across field, logistics, shelter, medical, weather, and volunteer channels.
- Calls MCP-compatible tools for weather, shelters, resources, hospitals, route risk, and audit logging.
- Computes a deterministic 0-100 risk score from seven explicit factors.
- Generates a response plan and safety review.
- Posts a Block Kit incident card with evidence, confidence, resources, and five actions.
- Requires a human to Approve, Request Revision, or Escalate.
- Persists incidents, evidence, plans, approvals, and audit events in shared SQLite storage.
- Shows the same incident store in a transparent Streamlit operational command center.

## How We Built It

The existing RescueNet AI backend was preserved and wrapped with Slack-native modules:

- `backend/main.py`: FastAPI API, health checks, Slack event route, demo endpoints, A2A, and legacy RescueNet routes.
- `slack_app/`: Slack Bolt app, slash command routing, App Home, app mention handling, actions, Block Kit, and context search abstraction.
- `rescuenet_slack/`: incident extraction, deterministic risk engine, response planning, safety review, SQLite store, and audit logging.
- `mcp_server/`: MCP-compatible local tool facade and standalone FastAPI MCP smoke endpoint.
- `command_center/`: Streamlit operational command center reading the same SQLite incident store for transparency.

## Slack Technology Usage

- Slack Bolt for Python.
- Slash command: `/rescuenet`.
- Global shortcut: `report_incident` opens an Incident Report modal.
- App mention event: `@RescueNet`.
- App Home: recent incidents and quick commands.
- Block Kit: incident card, fields, context blocks, and action buttons.
- Interactivity: Approve Response Plan, Request Revision, Escalate to Commander, View Evidence, Refresh Context.
- Modal: View Evidence opens an evidence modal.
- Public Request URL: `/slack/events` on the deployed FastAPI backend.
- Socket Mode: supported by `python -m slack_app.app` when `SLACK_APP_TOKEN` is set.

## MCP Usage

Current status: local MCP-compatible demo facade. It is functional and clearly labeled as demo data.

Implemented tools:

- `get_weather_alert`
- `get_shelter_capacity`
- `get_available_resources`
- `get_hospital_status`
- `get_route_risk`
- `log_incident_action`

Standalone MCP smoke server:

```bash
uvicorn mcp_server.server:mcp_app --host 127.0.0.1 --port 8011
```

## RTS / Context Search Usage

Current status: demo adapter labeled `mock_rts_search`.

The adapter reads `data/slack_demo_messages.json` and returns related incident threads, field reports, and resource mentions. It is not claimed as live Slack Real-Time Search. The upgrade path is documented in `docs/RTS_INTEGRATION.md`.

## Real Integrations vs Demo Adapters

| Component | Status | Notes |
|---|---|---|
| Slack slash command, App Home, mentions, interactivity | Implemented | Requires Slack app credentials and `/slack/events` configuration |
| Slack Real-Time Search / RTS | Demo adapter | `mock_rts_search`, upgrade path documented |
| MCP tools | Local demo facade | Functional local tool layer, upgrade path documented |
| Deterministic risk engine | Implemented | Seven-factor score, no hidden LLM scoring |
| SQLite incident store | Implemented | Shared by Slack and Streamlit |
| Streamlit command center | Implemented | Transparent operational view; Slack remains the primary UX |
| LLM reasoning | Optional | Demo works without API keys |
| Live public APIs | Optional opt-in | `USE_LIVE_APIS=false` by default for deterministic judging |

## Challenges

- Keeping Slack as the primary disaster-coordination UX while preserving the existing RescueNet backend.
- Making demo mode deterministic and fast without overstating live external integrations.
- Ensuring risk scoring is auditable rather than hidden behind an LLM.
- Sharing state cleanly between Slack actions and the Streamlit command center.

## Accomplishments

- A full Slack-native incident loop from field report to human approval.
- Functional Block Kit card with five operational actions.
- Shared SQLite persistence for incidents, evidence, plans, approvals, and audit events.
- Deterministic risk scoring with test coverage.
- Fast local test suite and deployment-ready backend route for Slack events.

## What We Learned

Emergency-response agents need strong boundaries: evidence should be visible, demo adapters must be labeled, and humans must approve operational plans. Slack is a strong command surface because it keeps responders inside the conversation where the incident started.

## Responsible AI

RescueNet Slack is decision support only. It never dispatches resources, never contacts emergency services, and never marks a plan approved without a human action. Incident cards show confidence, data sources, and a notice that human responders and emergency authorities retain final control.

## What's Next

- Connect approved Slack Real-Time Search access.
- Replace local MCP demo tools with live MCP-backed weather, shelter, GIS, and resource systems.
- Move SQLite to managed Postgres for multi-instance production deployments.
- Add signed commander roles and stricter approval permissions.
- Record and attach the 3-minute demo video.

## Tech Stack

Python, FastAPI, Slack Bolt for Python, Pydantic v2, LangGraph with sequential fallback, SQLite, Streamlit, Docker, pytest.
