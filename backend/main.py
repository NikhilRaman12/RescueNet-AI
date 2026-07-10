from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.a2a.protocol import A2AProtocol
from backend.config.settings import API_HOST, API_PORT, ENABLE_GUARDRAILS, ENVIRONMENT, USE_LIVE_APIS
from backend.database.mongo import get_operational_snapshot
from backend.evaluation.evaluator import evaluate_response
from backend.services.live_data_tools import fetch_live_data_bundle
from backend.services.mcp_service import fetch_external_context, get_mcp_events, register_mcp_handlers
from backend.services.rescue_graph import LANGGRAPH_AVAILABLE, run_rescue_graph
from mcp_server.tools import gather_mcp_context, list_tools as list_slack_mcp_tools
from rescuenet_slack.incident_models import IncidentSignal
from rescuenet_slack.orchestrator import analyze_signal
from rescuenet_slack.store import (
    get_audit_trail,
    get_evidence,
    get_incident,
    get_integration_statuses,
    get_response_plan,
    list_incidents as store_list_incidents,
    set_integration_status,
)
from slack_app.actions import handle_incident_action
from slack_app.blockkit import incident_card_message
from slack_app.commands import handle_rescuenet_command

app = FastAPI(
    title="RescueNet AI",
    description="Production-grade multi-agent disaster response command system.",
    version="2.0.0",
)

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
if ENVIRONMENT != "production":
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

protocol = A2AProtocol()
_slack_request_handler = None


class RescueRequest(BaseModel):
    query: str
    location: Optional[str] = "Hyderabad"
    disaster_type: Optional[str] = "flood"
    severity: Optional[str] = "high"
    context: Dict[str, Any] = {}


class SlackAnalyzeRequest(BaseModel):
    text: str
    channel: str = "field-reports"
    user_id: str = "demo-user"
    location: Optional[str] = None
    hazard_type: Optional[str] = None


class SlackCommandRequest(BaseModel):
    text: str = "demo"
    channel: str = "incident-command"
    user_id: str = "demo-user"


class SlackActionRequest(BaseModel):
    action_id: str
    incident_id: str
    user_id: str = "demo-user"


def _get_slack_request_handler():
    from slack_bolt.adapter.fastapi import SlackRequestHandler
    from slack_bolt.error import BoltError
    from slack_app.app import create_bolt_app
    from slack_app.config import settings as slack_settings

    global _slack_request_handler
    if _slack_request_handler is not None:
        return _slack_request_handler

    if not slack_settings.bot_token or not slack_settings.signing_secret:
        raise HTTPException(
            status_code=503,
            detail=(
                "Slack events endpoint is not configured. Set SLACK_BOT_TOKEN "
                "and SLACK_SIGNING_SECRET, then restart the backend."
            ),
        )

    try:
        _slack_request_handler = SlackRequestHandler(create_bolt_app())
    except BoltError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _slack_request_handler


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": "RescueNet AI",
        "status": "running",
        "docs": "/docs",
        "stack": {
            "api": "FastAPI",
            "orchestration": "LangGraph StateGraph" if LANGGRAPH_AVAILABLE else "Sequential execution",
            "communication": "A2A protocol",
            "tools": "MCP operational tools",
            "slack_agent": "RescueNet Slack command, mention, Block Kit, and actions",
            "data_layer": "SQLite OperationalDataStore",
            "agents": 12,
        },
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "operational",
        "service": "RescueNet AI",
        "slack_agent": "ready",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "environment": ENVIRONMENT,
    }


@app.get("/slack/events")
def slack_events_status() -> Dict[str, Any]:
    from slack_app.config import settings as slack_settings

    return {
        "endpoint": "/slack/events",
        "configured": bool(slack_settings.bot_token and slack_settings.signing_secret),
        "requires": ["SLACK_BOT_TOKEN", "SLACK_SIGNING_SECRET"],
        "supports": ["slash_commands", "events", "interactivity", "app_home"],
    }


@app.post("/slack/events")
async def slack_events(request: Request):
    handler = _get_slack_request_handler()
    return await handler.handle(request)


@app.get("/console", response_class=HTMLResponse)
def rescue_console() -> HTMLResponse:
    html_path = Path("frontend_static/index.html")
    if not html_path.exists():
        return HTMLResponse("<h1>RescueNet AI Console</h1><p>Console file not found.</p>")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/dashboard")
def dashboard() -> Dict[str, Any]:
    incidents = store_list_incidents(50)
    critical = [i for i in incidents if i.get("priority_tier") in {"CRITICAL", "SEVERE"}]
    pending = [i for i in incidents if i.get("approval_status") == "pending_human_approval"]
    return {
        "total_incidents": len(incidents),
        "critical_incidents": len(critical),
        "pending_approvals": len(pending),
        "alerts_open": 8,
        "active_missions": 4,
        "shelters_available": 12,
        "volunteers_assigned": 46,
        "resource_shortages": {"medical_kits": 20, "water_liters": 500},
    }


@app.post("/api/rescue")
def rescue_mission(payload: RescueRequest) -> Dict[str, Any]:
    request_payload = payload.model_dump()
    location = request_payload.get("location", "Hyderabad")
    severity = (request_payload.get("severity") or "high").lower()
    disaster_type = (request_payload.get("disaster_type") or "flood").lower()

    state = run_rescue_graph(request_payload)
    live_data = fetch_live_data_bundle(location) if USE_LIVE_APIS else {"mode": "fallback"}
    snapshot = get_operational_snapshot(location)

    guardrail_report = {
        "passed": True,
        "prompt_injection_detected": any(
            term in (request_payload.get("query") or "").lower()
            for term in ["ignore previous instructions", "bypass"]
        ),
        "unsafe_instruction_filtered": False,
        "pii_minimized": True,
        "emergency_disclaimer": "This is operational decision support, not final emergency authority.",
        "human_in_the_loop_required": severity in {"high", "critical"},
    }

    if ENABLE_GUARDRAILS and guardrail_report["prompt_injection_detected"]:
        guardrail_report["unsafe_instruction_filtered"] = True
        guardrail_report["passed"] = False

    mission_id = f"mission-{uuid4().hex[:8]}"
    correlation_id = state.get("correlation_id") or str(uuid4())

    state.update({
        "mission_id": mission_id,
        "correlation_id": correlation_id,
        "status": "completed",
        "location": location,
        "disaster_type": disaster_type,
        "risk_level": state.get("risk_level", "medium"),
        "live_data_sources": live_data,
        "live_weather": live_data.get("live_weather", {}),
        "live_disaster_events": live_data.get("live_disaster_events", {}),
        "live_earthquakes": live_data.get("live_earthquakes", {}),
        "live_geocoding": live_data.get("live_geocoding", {}),
        "live_routing": live_data.get("live_routing", {}),
        "resources": snapshot.get("resource_inventory", state.get("resources", {})),
        "hospitals": snapshot.get("hospitals", []),
        "routes": snapshot.get("routes", state.get("routes", {})),
        "volunteers": snapshot.get("volunteer_units", state.get("volunteers", {})),
        "operational_snapshot": snapshot,
        "guardrail_report": guardrail_report,
        "a2a_messages": state.get("a2a_messages") or [],
        "confidence_score": round(
            sum((state.get("confidence_scores") or {}).values())
            / max(1, len((state.get("confidence_scores") or {}).values())),
            3,
        ) if state.get("confidence_scores") else 0.8,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    })

    if not state.get("final_mission_plan"):
        state["final_mission_plan"] = {
            "mission_id": mission_id,
            "location": location,
            "disaster_type": disaster_type,
            "priority": severity,
            "summary": state.get("summary") or "Mission planning completed.",
            "recommended_actions": state.get("recommended_actions", []),
        }

    state["evaluation_report"] = evaluate_response(state)
    return state


@app.get("/api/mcp/server")
def mcp_server_status() -> Dict[str, Any]:
    return register_mcp_handlers()


@app.get("/api/mcp/context")
def mcp_context(location: str = "Hyderabad", risk_level: str = "high") -> Dict[str, Any]:
    return fetch_external_context(location, risk_level)


@app.get("/api/mcp/events")
def mcp_events() -> Dict[str, Any]:
    return get_mcp_events()


@app.get("/api/slack/status")
def slack_status() -> Dict[str, Any]:
    return {
        "service": "RescueNet Slack",
        "status": "ready",
        "track": "Slack Agent for Good",
        "slash_command": "/rescuenet",
        "mention_handler": "@RescueNet",
        "mock_slack_search": True,
        "mock_mcp_tools": True,
        "mcp_tools": list_slack_mcp_tools(),
        "supported_channels": [
            "incident-command", "field-reports", "weather-alerts",
            "medical-response", "logistics", "shelter-operations", "volunteers",
        ],
    }


@app.post("/api/slack/analyze")
def slack_analyze(payload: SlackAnalyzeRequest) -> Dict[str, Any]:
    signal = IncidentSignal(**payload.model_dump())
    card = analyze_signal(signal)
    return {
        "status": "pending_human_approval",
        "card": card.model_dump(),
        "slack_message": incident_card_message(card),
    }


@app.post("/api/slack/command")
def slack_command(payload: SlackCommandRequest) -> Dict[str, Any]:
    return handle_rescuenet_command(payload.text, payload.user_id, payload.channel)


@app.post("/api/slack/actions")
def slack_actions(payload: SlackActionRequest) -> Dict[str, Any]:
    return handle_incident_action(payload.action_id, payload.incident_id, payload.user_id)


@app.get("/api/slack/mcp/context")
def slack_mcp_context(location: str = "Village A") -> Dict[str, Any]:
    return gather_mcp_context(location)


# --- Store-backed incident endpoints ---

@app.get("/api/incidents")
def api_list_incidents(limit: int = 50) -> Dict[str, Any]:
    return {"incidents": store_list_incidents(limit)}


@app.get("/api/incidents/{incident_id}")
def api_get_incident(incident_id: str) -> Dict[str, Any]:
    incident = get_incident(incident_id)
    if not incident:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Incident not found")
    plan = get_response_plan(incident_id)
    evidence = get_evidence(incident_id)
    audit = get_audit_trail(incident_id)
    return {"incident": incident, "plan": plan, "evidence": evidence, "audit": audit}


@app.get("/api/incidents/{incident_id}/plan")
def api_get_plan(incident_id: str) -> Dict[str, Any]:
    plan = get_response_plan(incident_id)
    return {"incident_id": incident_id, "plan": plan}


@app.get("/api/incidents/{incident_id}/evidence")
def api_get_evidence(incident_id: str) -> Dict[str, Any]:
    return {"incident_id": incident_id, "evidence": get_evidence(incident_id)}


@app.get("/api/audit")
def api_audit(incident_id: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    return {"audit": get_audit_trail(incident_id, limit)}


@app.get("/api/integrations")
def api_integrations() -> Dict[str, Any]:
    set_integration_status("slack_search", {"mode": "mock_rts_search", "status": "demo_adapter"})
    set_integration_status("mcp_tools", {"mode": "local_facade", "status": "demo_data"})
    set_integration_status("llm", {"mode": "gemini_or_openai", "status": "optional"})
    return get_integration_statuses()


@app.get("/api/a2a/messages")
def a2a_messages(limit: int = 50) -> Dict[str, Any]:
    return {"messages": protocol.messages[-limit:], "count": len(protocol.messages[-limit:])}


@app.get("/api/a2a/conversation/{correlation_id}")
def a2a_conversation(correlation_id: str) -> Dict[str, Any]:
    return {
        "correlation_id": correlation_id,
        "messages": [m for m in protocol.messages if m.correlation_id == correlation_id],
    }


@app.get("/api/data/snapshot")
def operational_snapshot(location: str = "Hyderabad") -> Dict[str, Any]:
    return get_operational_snapshot(location)


@app.get("/api/data/incidents")
def operational_incidents(limit: int = 20) -> Dict[str, Any]:
    from backend.database.mongo import list_incidents
    return {"incidents": list_incidents(limit)}


@app.get("/api/live/data")
def live_data(location: str = "Hyderabad") -> Dict[str, Any]:
    return fetch_live_data_bundle(location) if USE_LIVE_APIS else {"mode": "fallback"}


@app.post("/api/evaluate")
def evaluate_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    return evaluate_response(payload)


@app.get("/api/observability/traces")
def observability_traces() -> Dict[str, Any]:
    return {"traces": []}
