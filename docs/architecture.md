# Existing RescueNet responder architecture

This document describes the pre-existing Slack/incident-response subsystem. It is not the architecture of the ReadyAtHome simulated experience. The current ReadyAtHome flow is documented in README.md and docs/SUBMISSION.md.

The existing RescueNet Slack flow retains a FastAPI backend and wraps it with Slack command, event, and approval handlers. The Streamlit Command Center provides an operational view over the local incident store. Slack and public-data connections require separate configuration; their demo adapters are not live data.

## Existing high-level flow

~~~text
Slack command or mention
  -> slack_app parsing and handlers
  -> rescuenet_slack incident extraction
  -> demo Slack-context search
  -> local MCP-named tool facade
  -> legacy LangGraph responder workflow
  -> deterministic incident-priority scoring
  -> draft response plan and safety review
  -> human approval through Slack actions
  -> existing SQLite and JSONL audit paths
~~~

## ReadyAtHome flow

~~~text
Browser text request
  -> frontend/src/readyathome.tsx
  -> POST /api/readiness/plan
  -> readyathome.service deterministic intent and checklist
  -> explainable plan, assumptions, source links, integration labels
  -> browser local storage for task flags
  -> POST /api/readiness/tasks/{task_id}
  -> rescuenet_slack.store audit_events table
~~~

ReadyAtHome does not call Slack, LangGraph, the responder risk engine, MCP-named tools, live data adapters, or a language model. The typed contracts are in readyathome/models.py; routes are in backend/routers/readiness.py.

## Preserved responder components

- backend/main.py: existing FastAPI endpoints plus the ReadyAtHome router.
- backend/services/rescue_graph.py: legacy multi-agent incident-response workflow.
- slack_app/: Slack commands, events, Block Kit, action handlers, and demo context search.
- rescuenet_slack/: incident extraction, risk scoring, plan generation, audit persistence, and orchestration.
- mcp_server/: existing local demo tool facade; not a verified remote MCP server.
- command_center/: existing Streamlit operations pages.
- frontend/src/App.tsx: existing React incident command center, still served from the root Vite page.

Live public-data adapters are disabled by default after this work; USE_LIVE_APIS=true explicitly opts into the legacy adapters. They are never used in ReadyAtHome.
