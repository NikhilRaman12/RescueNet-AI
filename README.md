# 🚨 RescueNet Slack

> Autonomous Crisis Operations Agent for Slack — *Slack Agent for Good*

**Primary UX:** Slack App / Slack Agent  
**Secondary UX:** [Streamlit Command Center](#streamlit-command-center) — deploy to Streamlit Community Cloud or Hugging Face Spaces  
**GitHub:** https://github.com/NikhilRaman12/RescueNet-AI  
**Track:** Slack Agent for Good  

---

## Problem

During floods, cyclones, and earthquakes, critical updates are scattered across Slack channels — field reports, shelter notes, weather alerts, resource messages. Incident commanders make life-or-death decisions without a shared operational picture. Teams lose minutes searching for context that already exists in their own Slack workspace.

## Impact

RescueNet Slack gives response teams a shared operational loop in seconds:

| Before | After |
|---|---|
| Commander reads 5 channels manually | Agent searches all channels instantly |
| No structured severity score | Deterministic 0–100 score across 7 factors |
| Resources dispatched without verification | Human approval required before any action |
| No audit trail | Every decision logged to SQLite + JSONL |
| Scattered context | Single Block Kit incident card with all evidence |

---

## Slack Workflow

```
Field report posted in #field-reports
  │
  ▼
/rescuenet analyze "Flood water crossed bridge near Village A.
                    70 people stranded, elderly and children present."
  │
  ├─► Incident Detection Agent
  │     extracts: location, hazard, people, vulnerable groups, urgency
  │
  ├─► Slack Context Intelligence Agent  [mock_rts_search]
  │     searches: #field-reports, #logistics, #shelter-operations,
  │               #weather-alerts, #medical-response
  │
  ├─► Hazard Intelligence Agent  [MCP: get_weather_alert]
  │     returns: high risk, 96mm rainfall, rising river
  │
  ├─► Resource Discovery Agent  [MCP: get_shelter_capacity, get_available_resources]
  │     returns: Shelter C (140 spaces), Boat Team 2 (available)
  │
  ├─► Risk & Priority Agent  [deterministic 0-100]
  │     score: 79/100  →  SEVERE priority
  │     factors: large population, vulnerable groups, high hazard,
  │              blocked routes, corroborating Slack threads
  │
  ├─► Response Planning Agent
  │     actions: dispatch boat team, open Shelter C, stage ambulance
  │
  ├─► Verification/Safety Agent
  │     confidence: 87%  |  human_approval_required: true
  │
  ▼
Block Kit Incident Card posted in #incident-command
  │
  ├─► [✅ Approve Response Plan]
  ├─► [✏️ Request Revision]
  ├─► [🚨 Escalate to Commander]
  ├─► [🔍 View Evidence]  →  opens modal with Slack + MCP sources
  └─► [🔄 Refresh Context]  →  re-runs full pipeline
  │
  ▼
Human approves → audit trail updated → SQLite + JSONL
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Slack Workspace                          │
│  /rescuenet <cmd>   @RescueNet <text>   App Home   Buttons      │
└────────────────────────────┬────────────────────────────────────┘
                             │ Slack Bolt for Python
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      slack_app/                                 │
│  commands.py   events.py   actions.py   blockkit.py   app.py    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   rescuenet_slack/                              │
│  orchestrator.py → risk_engine.py → response_planner.py        │
│  safety.py       → store.py (SQLite) → audit_log.py (JSONL)    │
└──────────┬──────────────────────────────────────┬──────────────┘
           │                                      │
           ▼                                      ▼
┌──────────────────────┐              ┌───────────────────────────┐
│   slack_app/         │              │   mcp_server/tools.py     │
│   context_search.py  │              │                           │
│   [mock_rts_search]  │              │  get_weather_alert()      │
│   data/slack_demo_   │              │  get_shelter_capacity()   │
│   messages.json      │              │  get_available_resources()│
└──────────────────────┘              │  get_hospital_status()    │
                                      │  get_route_risk()         │
                                      │  log_incident_action()    │
                                      └───────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│              backend/services/rescue_graph.py                   │
│              LangGraph multi-agent workflow (10 agents)         │
│  DisasterIntelligence → PriorityScoring → DamageAssessment     │
│  ShelterCoordination → RouteOptimization → ResourceAllocation  │
│  MedicalTriage → VolunteerCoordination → Alert → MissionPlanner│
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  data/rescuenet.db  (SQLite)                    │
│  incidents │ evidence │ response_plans │ approvals │ audit      │
│                                                                 │
│  ← read by Slack app (FastAPI)  AND  Streamlit command center   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Risk Scoring — Deterministic 0–100

LLM may explain the score but **never secretly decides it**. Score is computed from 7 explicit factors:

| Factor | Max Points | What triggers it |
|---|---|---|
| People affected | 20 | ≥50 people → 16pts, ≥100 → 20pts |
| Vulnerable groups | 15 | elderly/children/disabled/pregnant |
| Medical urgency | 12 | injured/ambulance/bleeding keywords |
| Hazard severity | 15 | weather risk level + hazard type |
| Escalation trend | 10 | corroborating Slack thread count |
| Access constraints | 15 | blocked routes from MCP route tool |
| Resource gap | 13 | shortages + shelter capacity vs people |
| **Total** | **100** | |

Priority tiers: `LOW` (0–29) · `MODERATE` (30–49) · `HIGH` (50–69) · `SEVERE` (70–84) · `CRITICAL` (85–100)

---

## Slack Commands

| Command | Description |
|---|---|
| `/rescuenet help` | Show command reference |
| `/rescuenet demo` | Run Village A flood demo (deterministic, no API keys needed) |
| `/rescuenet analyze <text>` | Analyze any field report |
| `/rescuenet status` | Agent and integration status |
| `/rescuenet incidents` | List recent incidents from store |
| `/rescuenet resources <location>` | Resource lookup via MCP |
| `/rescuenet plan <incident_id>` | View response plan for an incident |

---

## MCP Integration

**Status: local demo facade** — clearly labeled, not claimed as live.

| Tool | Demo Source | Upgrade Path |
|---|---|---|
| `get_weather_alert(location)` | `data/weather_demo.json` | Point to live weather API |
| `get_shelter_capacity(location)` | `data/shelters_demo.json` | Point to shelter registry |
| `get_available_resources(location)` | `data/resources_demo.json` | Point to resource management system |
| `get_hospital_status(location)` | Inline demo data | Point to hospital API |
| `get_route_risk(location)` | Inline demo data | Point to routing/GIS API |
| `log_incident_action(id, action)` | SQLite + JSONL | Already persistent |

To connect a real MCP server, update `TOOL_REGISTRY` in `mcp_server/tools.py`.  
See `docs/MCP_INTEGRATION.md` for full upgrade instructions.

---

## Slack Real-Time Search / Context Search

**Status: demo adapter** — mode labeled `mock_rts_search` in all responses.

| Function | What it does | Demo source |
|---|---|---|
| `search_slack_context(query, channels, time_window)` | Full-text search across Slack messages | `data/slack_demo_messages.json` |
| `retrieve_related_incident_threads(location, hazard)` | Find corroborating incident threads | Same |
| `retrieve_latest_field_reports(location)` | Latest field reports | Same |
| `retrieve_resource_mentions(location)` | Logistics and resource mentions | Same |

To connect live Slack Real-Time Search, replace `search_slack_context` in `slack_app/context_search.py` with the Slack SDK search call.  
See `docs/RTS_INTEGRATION.md` for full upgrade instructions.

---

## Integration Matrix

| Component | Status | Notes |
|---|---|---|
| Slack slash command `/rescuenet` | ✅ Implemented | 7 sub-commands |
| Slack App Home | ✅ Implemented | Recent incidents list |
| `@RescueNet` mention handler | ✅ Implemented | Full pipeline on mention |
| Incident report modal | ✅ Implemented | Global shortcut `report_incident` |
| Block Kit incident cards | ✅ Implemented | Priority tier badge, 5 buttons |
| Interactive buttons | ✅ Implemented | Approve, Revise, Escalate, Evidence, Refresh |
| Evidence modal | ✅ Implemented | View Evidence button opens modal |
| Slack Real-Time Search | 🟡 Demo adapter | `mock_rts_search` — upgrade path documented |
| MCP tools | 🟡 Demo facade | 6 tools, demo data labeled — upgrade path documented |
| LLM reasoning | 🟡 Optional | Set `GEMINI_API_KEY` or `OPENAI_API_KEY` |
| Deterministic risk scoring | ✅ Live | 0–100, 7 factors, no LLM dependency |
| SQLite incident store | ✅ Live | Shared by Slack + Streamlit |
| Human approval workflow | ✅ Live | Required before any action |
| Audit trail | ✅ Live | SQLite + JSONL |
| LangGraph multi-agent graph | ✅ Live | 10 agents, sequential fallback |
| Streamlit command center | ✅ Live | 5 tabs, same SQLite store |
| Docker / Docker Compose | ✅ Live | Single `docker compose up --build` |
| Test suite | ✅ 48/48 passing | Risk scoring, store, commands, modal, Block Kit, MCP, RTS, Slack route readiness |

---

## Safety Boundary

> **RescueNet Slack is decision support only.**

- The agent **never dispatches resources automatically**
- The agent **never contacts emergency services**
- Every generated plan requires **explicit human approval** before any action
- Every incident card shows: confidence score, data sources, unsupported claims, and the notice: *"Decision support only. Human responders and emergency authorities retain final control."*
- If confidence is below threshold or resource availability is uncertain, the plan explicitly asks for verification before action
- All decisions are written to an immutable audit trail

---

## Local Setup

```bash
git clone https://github.com/NikhilRaman12/RescueNet-AI.git
cd RescueNet-AI
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

Open:
- API health: http://127.0.0.1:8010/health
- API docs: http://127.0.0.1:8010/docs
- Slack agent status: http://127.0.0.1:8010/api/slack/status

---

## Demo Commands

**Village A flood demo (no API keys needed):**

```bash
# Run demo
curl -X POST "http://127.0.0.1:8010/api/slack/command" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"demo\",\"channel\":\"incident-command\",\"user_id\":\"U-demo\"}"

# Analyze custom report
curl -X POST "http://127.0.0.1:8010/api/slack/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Flood water crossed bridge near Village A. 70 people stranded, elderly and children present.\",\"channel\":\"field-reports\",\"user_id\":\"U-demo\"}"

# Approve (replace <incident_id> from previous response)
curl -X POST "http://127.0.0.1:8010/api/slack/actions" \
  -H "Content-Type: application/json" \
  -d "{\"action_id\":\"approve_response_plan\",\"incident_id\":\"<incident_id>\",\"user_id\":\"U-commander\"}"

# List all incidents
curl "http://127.0.0.1:8010/api/incidents"

# MCP context
curl "http://127.0.0.1:8010/api/slack/mcp/context?location=Village+A"
```

**Streamlit command center:**

```bash
streamlit run streamlit_app.py
# Opens: http://localhost:8501
```

**Slack Bolt app (requires Slack credentials):**

```bash
python -m slack_app.app
```

---

## Streamlit Command Center

Secondary deployed demo surface. Reads from the same SQLite store as the Slack app.

Tabs: **Incidents** | **Analyze** | **Audit Trail** | **Integrations** | **Architecture**

Deploy to Streamlit Community Cloud:
1. Go to https://share.streamlit.io
2. Repo: `NikhilRaman12/RescueNet-AI`, Branch: `main`, File: `streamlit_app.py`
3. Add secrets: `USE_MOCK_SLACK_SEARCH="true"`, `USE_MOCK_MCP_TOOLS="true"`, `APP_ENV="production"`

Deploy to Hugging Face Spaces:
1. New Space → SDK: Streamlit → App file: `streamlit_app.py`
2. Same secrets as above

---

## Slack App Setup

See `docs/slack_setup.md` for full instructions. Summary:

1. Create app at https://api.slack.com/apps
2. Add scopes: `commands`, `chat:write`, `app_mentions:read`, `channels:history`
3. Add slash command `/rescuenet` pointing to your deployed backend `/slack/events`
4. Enable Event Subscriptions: `app_mention`, `app_home_opened`
5. Enable Interactivity pointing to `/slack/events`
6. Set env vars: `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_SIGNING_SECRET`

---

## Backend Deployment

**Render (recommended for hackathon):**
- Build: `pip install -r requirements.txt`
- Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Env: `APP_ENV=production`, `USE_MOCK_SLACK_SEARCH=true`, `USE_MOCK_MCP_TOOLS=true`

**Docker:**
```bash
docker compose up --build
# Backend: http://localhost:8010
```

See `deployment/render.md`, `deployment/cloud_run.md` for full guides.

---

## Environment Variables

```text
SLACK_BOT_TOKEN=          # xoxb-... from Slack app
SLACK_APP_TOKEN=          # optional xapp-... for Socket Mode
SLACK_SIGNING_SECRET=     # from Slack app Basic Information
SLACK_CLIENT_ID=
SLACK_CLIENT_SECRET=
OPENAI_API_KEY=           # optional — for LLM-enhanced reasoning
GEMINI_API_KEY=           # optional — for LLM-enhanced reasoning
RESCUENET_LLM_MODEL=      # optional
USE_MOCK_SLACK_SEARCH=true
USE_MOCK_MCP_TOOLS=true
APP_ENV=development
USE_LIVE_APIS=false       # set true only when public API calls have been verified
ENABLE_GUARDRAILS=true
API_HOST=0.0.0.0
API_PORT=8010
```

No secrets are committed. Demo mode works with all values empty.

---

## Testing

```bash
python -m pytest
# 48 tests, all passing
```

Covers: priority tiers, risk scoring (all 7 factors), all 7 slash commands, incident modal, Block Kit card structure (all 5 buttons), human approval workflow, store persistence, MCP tools, context search adapter, audit trail, dashboard endpoint.

---

## Repository Map

```
backend/              Existing RescueNet AI — FastAPI, LangGraph, 10 agents, A2A protocol
rescuenet_slack/      Incident extraction, risk scoring, response planning, safety, store
slack_app/            Slack Bolt app, commands, events, actions, blockkit, context search
mcp_server/           MCP-compatible local tool facade (6 tools)
command_center/       Streamlit secondary command center (5 tabs)
data/                 Demo Slack messages, shelters, resources, weather, SQLite DB
docs/                 architecture, slack_setup, MCP_INTEGRATION, RTS_INTEGRATION,
                      demo_script, SUBMISSION, JUDGING_ALIGNMENT
deployment/           Render, Cloud Run, Hugging Face Spaces, Streamlit Cloud guides
tests/                48 tests - all passing
```

---

## Screenshots

> Add screenshots to `screenshots/` and link here after recording the demo video.

| Screen | File |
|---|---|
| App Home — recent incidents | `screenshots/app_home.png` |
| Block Kit incident card | `screenshots/incident_card.png` |
| Evidence modal | `screenshots/evidence_modal.png` |
| Streamlit Incidents tab | `screenshots/streamlit_incidents.png` |
| Streamlit Analyze tab | `screenshots/streamlit_analyze.png` |
| Audit trail | `screenshots/audit_trail.png` |

---

## Demo Video

> Record a <=3-minute video following `docs/demo_script.md` and add the link here.

**Demo video:** _[add YouTube/Loom link after recording]_

Script: `docs/demo_script.md`
