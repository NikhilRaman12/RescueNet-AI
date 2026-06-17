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
def rescue(req: RescueRequest):
    result = run_rescue_graph(req.model_dump())
    return {
        "mission_status": "response_plan_generated",
        "risk_level": result.get("risk_level", "medium"),
        "summary": result.get("summary"),
        "agents_used": result.get("agents_used", []),
        "a2a_trace": result.get("a2a_trace", []),
        "a2a_messages": result.get("a2a_messages", []),
        "disaster_analysis": result.get("disaster_analysis", {}),
        "priority_score": result.get("priority_score", {}),
        "damage_assessment": result.get("damage_assessment", {}),
        "shelters": result.get("shelters", []),
        "routes": result.get("routes", {}),
        "resources": result.get("resources", {}),
        "resource_priority": result.get("resource_priority", []),
        "medical_triage": result.get("medical_triage", {}),
        "volunteers": result.get("volunteers", {}),
        "public_alert": result.get("public_alert", {}),
        "recommended_actions": result.get("recommended_actions", []),
    }


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
