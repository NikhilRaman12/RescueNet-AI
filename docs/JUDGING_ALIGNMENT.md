# Judging Alignment — RescueNet Slack

Track: Slack Agent for Good

---

## Criterion 1: Slack as Primary UX

| Requirement | Implementation |
|---|---|
| Slash command | `/rescuenet` with 7 sub-commands |
| Mention handler | `@RescueNet` via `app_mention` event |
| App Home | Recent incidents list, quick command reference |
| Block Kit cards | Priority tier badge, 6 sections, 5 action buttons |
| Interactive buttons | Approve, Revise, Escalate, View Evidence, Refresh Context |
| Modals | Incident Report shortcut modal and Evidence modal |
| Thread-ready | All responses include `response_type: in_channel` |

**File:** `slack_app/app.py`, `slack_app/commands.py`, `slack_app/blockkit.py`

---

## Criterion 2: Agent Capabilities

| Agent | Implementation |
|---|---|
| Incident Detection | `rescuenet_slack/orchestrator.py::extract_incident` |
| Slack Context Intelligence | `slack_app/context_search.py::build_slack_context` |
| Hazard Intelligence | `mcp_server/tools.py::get_weather_alert` |
| Resource Discovery | `mcp_server/tools.py::get_available_resources`, `get_shelter_capacity` |
| Risk & Priority | `rescuenet_slack/risk_engine.py::score_incident` (deterministic 0–100) |
| Response Planning | `rescuenet_slack/response_planner.py::build_response_plan` |
| Verification/Safety | `rescuenet_slack/safety.py::review_plan` |
| Incident Commander | `slack_app/actions.py::handle_incident_action` (human-in-the-loop) |
| Multi-Agent Graph | `backend/services/rescue_graph.py` (LangGraph, 10 agents) |

---

## Criterion 3: MCP Integration

- 6 MCP-compatible tools in `mcp_server/tools.py`
- `TOOL_REGISTRY` is replaceable with real MCP server
- All demo responses labeled with source field
- Standalone MCP server at `mcp_server/server.py`
- Upgrade path documented in `docs/MCP_INTEGRATION.md`

---

## Criterion 4: Slack Real-Time Search

- `search_slack_context`, `retrieve_related_incident_threads`, `retrieve_resource_mentions`, `retrieve_latest_field_reports` in `slack_app/context_search.py`
- Demo adapter uses `data/slack_demo_messages.json`
- Mode labeled `mock_rts_search` in all responses
- Escalation trend factor in risk scoring uses Slack context thread count
- Upgrade path documented in `docs/RTS_INTEGRATION.md`

---

## Criterion 5: Human-in-the-Loop Safety

- Agent never dispatches resources automatically
- Every incident card shows `human_approval_required: true`
- 5 action buttons: Approve, Revise, Escalate, View Evidence, Refresh Context
- All decisions written to SQLite audit trail + JSONL audit log
- Safety review includes confidence score, data sources, unsupported claims
- Decision support notice on every card

---

## Criterion 6: Impact and Use Case

- Target users: NGOs, field volunteers, incident commanders
- Problem: fragmented Slack updates during emergencies
- Solution: shared operational loop from field report to approved response plan
- Demo scenario: Village A flood — 70 people stranded, elderly and children
- Deterministic scoring ensures reproducible, auditable decisions

---

## Criterion 7: Code Quality and Architecture

- Existing RescueNet AI backend preserved (10 agents, LangGraph, A2A protocol)
- Clean separation: `backend/` (existing), `rescuenet_slack/` (new), `slack_app/` (new), `mcp_server/` (new)
- Pydantic v2 models throughout
- SQLite store shared between Slack and Streamlit
- Full test suite: 48 tests, all passing
- No secrets committed
- Docker and Docker Compose provided

---

## Criterion 8: Documentation

| Document | Location |
|---|---|
| README | `README.md` |
| Architecture | `docs/architecture.md` |
| Slack Setup | `docs/slack_setup.md` |
| MCP Integration | `docs/MCP_INTEGRATION.md` |
| RTS Integration | `docs/RTS_INTEGRATION.md` |
| Demo Script | `docs/demo_script.md` |
| Submission | `docs/SUBMISSION.md` |
| Judging Alignment | `docs/JUDGING_ALIGNMENT.md` |
| Deployment | `deployment/` |
