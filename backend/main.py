from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.services.rescue_graph import LANGGRAPH_AVAILABLE, run_rescue_graph
from backend.services.mcp_service import fetch_external_context, get_mcp_events, register_mcp_handlers
from backend.services.live_data_tools import fetch_live_data_bundle
from backend.a2a.protocol import get_a2a_conversation, get_a2a_messages


app = FastAPI(
    title="RescueNet AI",
    description="Autonomous Multi-Agent Disaster Response Operating System.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RescueRequest(BaseModel):
    query: str
    location: Optional[str] = "Hyderabad"
    disaster_type: Optional[str] = "flood"
    severity: Optional[str] = "high"
    context: Dict[str, Any] = {}


@app.get("/")
def root():
    return {
        "service": "RescueNet AI",
        "status": "running",
        "docs": "/docs",
        "console": "/console",
        "stack": {
            "api": "FastAPI",
            "orchestration": "LangGraph StateGraph" if LANGGRAPH_AVAILABLE else "Sequential execution",
            "communication": "A2A protocol",
            "tools": "MCP operational tools",
            "data_layer": "OperationalDataStore",
            "agents": 10,
        },
    }


@app.get("/health")
def health():
    return {
        "status": "OperationalOperational",
        "service": "RescueNet AI",
        "langgraph_available": LANGGRAPH_AVAILABLE,
    }


@app.get("/console", response_class=HTMLResponse)
def rescue_console():
    html_path = Path("frontend_static/index.html")
    if not html_path.exists():
        return HTMLResponse("<h1>RescueNet AI Console</h1><p>Console Console fileile not found.</p>")
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/dashboard")
def dashboard():
    return {
        "alerts_open": 8,
        "active_missions": 4,
        "shelters_available": 12,
        "volunteers_assigned": 46,
        "critical_incidents": 3,
        "resource_shortages": {"medical_kits": 20, "water_liters": 500},
    }


@app.post("/api/rescue")
def rescue_mission(payload: RescueRequest):
    request_payload = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    location = request_payload.get("location", "Hyderabad")
    severity = request_payload.get("severity", "High")
    disaster_type = request_payload.get("disaster_type", "Flood")

    state = run_rescue_graph(request_payload)
    live_data = fetch_live_data_bundle(location)
    try:
        snapshot = get_operational_snapshot(location)
    except Exception:
        snapshot = {}

    a2a_trace = state.get("a2a_trace", [])
    a2a_messages = state.get("a2a_messages") or [
        {
            "message_type": "handoff",
            "sequence": idx + 1,
            "detail": msg,
            "status": "sent",
            "location": location,
            "disaster_type": disaster_type.lower(),
            "priority": severity.lower(),
        }
        for idx, msg in enumerate(a2a_trace)
    ]

    state["location"] = location
    state["live_data_sources"] = live_data
    state["live_weather"] = live_data.get("live_weather", {})
    state["live_disaster_events"] = live_data.get("live_disaster_events", {})
    state["live_earthquakes"] = live_data.get("live_earthquakes", {})
    state["live_geocoding"] = live_data.get("live_geocoding", {})
    state["live_routing"] = live_data.get("live_routing", {})
    state["a2a_messages"] = a2a_messages

    # Override operational sections from selected city snapshot so no city falls back visually.
    state["resources"] = snapshot.get("resource_inventory", state.get("resources", {}))
    state["hospitals"] = snapshot.get("hospitals", [])
    state["routes"] = snapshot.get("routes", state.get("routes", {}))
    state["volunteers"] = snapshot.get("volunteer_units", state.get("volunteers", {}))
    state["operational_snapshot"] = snapshot

    if "disaster_analysis" in state:
        state["disaster_analysis"]["location"] = location

    if "public_alert" in state:
        state["public_alert"]["message"] = f"URGENT: High-risk emergency near {location}. Follow evacuation instructions and move to nearest safe shelter."

    state["a2a_messages"] = a2a_messages
    return state


@app.get("/api/mcp/server")
def mcp_server_status():
    return register_mcp_handlers()


@app.get("/api/mcp/context")
def mcp_context(location: str = "Hyderabad", risk_level: str = "high"):
    return fetch_external_context(location, risk_level)


@app.get("/api/mcp/events")
def mcp_events():
    return get_mcp_events()


@app.get("/api/a2a/messages")
def a2a_messages(limit: int = 50):
    return get_a2a_messages(limit)


@app.get("/api/a2a/conversation/{correlation_id}")
def a2a_conversation(correlation_id: str):
    return get_a2a_conversation(correlation_id)


@app.get("/api/data/snapshot")
def operational_snapshot(location: str = "Hyderabad"):
    from backend.database.mongo import get_operational_snapshot
    return get_operational_snapshot(location)


@app.get("/api/data/incidents")
def operational_incidents(limit: int = 20):
    from backend.database.mongo import list_incidents
    return {"incidents": list_incidents(limit)}


@app.get("/api/live/data")
def live_data(location: str = "Hyderabad"):
    return fetch_live_data_bundle(location)
