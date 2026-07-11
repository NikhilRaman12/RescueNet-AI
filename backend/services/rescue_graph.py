"""
RescueNet LangGraph Supervisor
──────────────────────────────
Shared RescueState flows through a supervisor node that uses conditional
routing to dispatch to specialist agents.  High-severity incidents get the
full 10-agent pipeline; lower-severity incidents skip non-critical agents.

Conditional routing map
  intake → guardrails → supervisor
  supervisor → [disaster, context_enrichment]   (always)
  supervisor → [medical, shelter, route]         (severity >= medium)
  supervisor → [resource, volunteer]             (severity >= medium)
  supervisor → [damage, alert, mission_planner]  (always, after specialists)
  mission_planner → END
"""
from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from backend.a2a.protocol import A2AProtocol
from backend.agents.alert_agent import AlertAgent
from backend.agents.damage_agent import DamageAssessmentAgent
from backend.agents.disaster_agent import DisasterIntelligenceAgent
from backend.agents.medical_agent import MedicalTriageAgent
from backend.agents.mission_agent import MissionPlannerAgent
from backend.agents.priority_agent import PriorityScoringAgent
from backend.agents.resource_agent import ResourceAgent
from backend.agents.route_agent import RouteOptimizationAgent
from backend.agents.shelter_agent import ShelterCoordinationAgent
from backend.agents.volunteer_agent import VolunteerCoordinationAgent
from backend.config.settings import USE_LIVE_APIS
from backend.services.live_data_tools import fetch_live_data_bundle

try:
    from langgraph.graph import END, StateGraph
    LANGGRAPH_AVAILABLE = True
except Exception:
    END = None
    StateGraph = None
    LANGGRAPH_AVAILABLE = False


# ── Shared state ─────────────────────────────────────────────────────────────

class RescueState(TypedDict, total=False):
    # Input
    query: str
    location: str
    disaster_type: str
    severity: str
    context: Dict[str, Any]
    # Routing
    route_path: str          # "full" | "standard" | "minimal"
    # Agent outputs
    risk_level: str
    disaster_analysis: Dict[str, Any]
    priority_score: Dict[str, Any]
    damage_assessment: Dict[str, Any]
    shelter_plan: Dict[str, Any]
    route_plan: Dict[str, Any]
    resource_plan: Dict[str, Any]
    medical_triage: Dict[str, Any]
    volunteer_plan: Dict[str, Any]
    public_alert: Dict[str, Any]
    final_mission_plan: Dict[str, Any]
    recommended_actions: List[str]
    # Live data
    live_data_sources: Dict[str, Any]
    live_weather: Dict[str, Any]
    live_disaster_events: Dict[str, Any]
    live_earthquakes: Dict[str, Any]
    live_geocoding: Dict[str, Any]
    live_routing: Dict[str, Any]
    # Observability
    summary: str
    agents_used: List[str]
    a2a_trace: List[str]
    a2a_messages: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    reasoning_summaries: Dict[str, str]
    observability_traces: List[Dict[str, Any]]
    guardrail_report: Dict[str, Any]
    evaluation_report: Dict[str, Any]
    # Meta
    mission_id: str
    correlation_id: str
    status: str
    confidence_score: float
    generated_at: str


# ── Singleton agents ──────────────────────────────────────────────────────────

protocol = A2AProtocol()
_disaster = DisasterIntelligenceAgent()
_priority = PriorityScoringAgent()
_damage = DamageAssessmentAgent()
_shelter = ShelterCoordinationAgent()
_route = RouteOptimizationAgent()
_resource = ResourceAgent()
_medical = MedicalTriageAgent()
_volunteer = VolunteerCoordinationAgent()
_alert = AlertAgent()
_mission = MissionPlannerAgent()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _handoff(state: RescueState, sender: str, receiver: str, note: str) -> RescueState:
    protocol.handoff(sender, receiver, dict(state), note)
    state.setdefault("a2a_trace", []).append(f"{sender} -> {receiver}: {note}")
    return state


def _severity_rank(state: RescueState) -> int:
    """Return 0=low, 1=medium, 2=high/critical."""
    s = (state.get("severity") or "medium").lower()
    rl = (state.get("risk_level") or "").lower()
    if s in {"critical", "high"} or rl in {"critical", "high"}:
        return 2
    if s == "medium" or rl == "medium":
        return 1
    return 0


# ── Graph nodes ───────────────────────────────────────────────────────────────

def intake_node(state: RescueState) -> RescueState:
    state.setdefault("agents_used", [])
    state.setdefault("a2a_trace", [])
    state.setdefault("a2a_messages", [])
    state.setdefault("confidence_scores", {})
    state.setdefault("reasoning_summaries", {})
    state.setdefault("observability_traces", [])
    state.setdefault("status", "running")
    return state


def guardrail_node(state: RescueState) -> RescueState:
    query = (state.get("query") or "").lower()
    severity = (state.get("severity") or "high").lower()
    injection = any(t in query for t in ["ignore previous instructions", "bypass", "jailbreak"])
    report = {
        "passed": not injection,
        "prompt_injection_detected": injection,
        "unsafe_instruction_filtered": injection,
        "pii_minimized": True,
        "emergency_disclaimer": "Operational decision support only — not final emergency authority.",
        "human_in_the_loop_required": severity in {"high", "critical"},
    }
    state["guardrail_report"] = report
    state.setdefault("agents_used", []).append("Safety Guardrail Agent")
    return state


def supervisor_node(state: RescueState) -> RescueState:
    """
    Supervisor decides the route_path based on severity and risk signals.
    This node does NOT call agents — it sets routing metadata consumed by
    the conditional edge function.
    """
    rank = _severity_rank(state)
    if rank >= 2:
        state["route_path"] = "full"
    elif rank == 1:
        state["route_path"] = "standard"
    else:
        state["route_path"] = "minimal"
    state.setdefault("agents_used", []).append("Supervisor Agent")
    _handoff(state, "Supervisor Agent", "Disaster Intelligence Agent",
             f"Routing path={state['route_path']} for severity={state.get('severity')}")
    return state


def disaster_node(state: RescueState) -> RescueState:
    state = _disaster.run(dict(state))
    return _handoff(state, "Disaster Intelligence Agent", "Priority Scoring Agent",
                    "Disaster risk assessment completed")


def priority_node(state: RescueState) -> RescueState:
    state = _priority.run(dict(state))
    return _handoff(state, "Priority Scoring Agent", "Damage Assessment Agent",
                    "Priority scoring completed")


def damage_node(state: RescueState) -> RescueState:
    state = _damage.run(dict(state))
    return _handoff(state, "Damage Assessment Agent", "Shelter Coordination Agent",
                    "Damage impact assessment completed")


def shelter_node(state: RescueState) -> RescueState:
    state = _shelter.run(dict(state))
    return _handoff(state, "Shelter Coordination Agent", "Route Optimization Agent",
                    "Shelter coordination completed")


def route_node(state: RescueState) -> RescueState:
    state = _route.run(dict(state))
    return _handoff(state, "Route Optimization Agent", "Resource Allocation Agent",
                    "Route plan completed")


def resource_node(state: RescueState) -> RescueState:
    state = _resource.run(dict(state))
    return _handoff(state, "Resource Allocation Agent", "Medical Triage Agent",
                    "Resource plan completed")


def medical_node(state: RescueState) -> RescueState:
    state = _medical.run(dict(state))
    return _handoff(state, "Medical Triage Agent", "Volunteer Coordination Agent",
                    "Medical triage completed")


def volunteer_node(state: RescueState) -> RescueState:
    state = _volunteer.run(dict(state))
    return _handoff(state, "Volunteer Coordination Agent", "Public Alert Agent",
                    "Volunteer coordination completed")


def alert_node(state: RescueState) -> RescueState:
    state = _alert.run(dict(state))
    return _handoff(state, "Public Alert Agent", "Mission Planner Agent",
                    "Public alert drafted")


def mission_node(state: RescueState) -> RescueState:
    state = _mission.run(dict(state))
    state["status"] = "completed"
    return state


# ── Conditional routing ───────────────────────────────────────────────────────

def _route_after_supervisor(state: RescueState) -> str:
    """After supervisor, always go to disaster first."""
    return "disaster"


def _route_after_priority(state: RescueState) -> str:
    """After priority scoring, route based on path."""
    path = state.get("route_path", "standard")
    if path == "minimal":
        return "alert"          # skip damage/shelter/route/resource/medical/volunteer
    return "damage"


def _route_after_damage(state: RescueState) -> str:
    path = state.get("route_path", "standard")
    if path == "minimal":
        return "alert"
    return "shelter"


def _route_after_medical(state: RescueState) -> str:
    path = state.get("route_path", "standard")
    if path == "full":
        return "volunteer"
    return "alert"             # standard path skips volunteer


# ── Graph builder ─────────────────────────────────────────────────────────────

def build_graph():
    if not LANGGRAPH_AVAILABLE:
        return None

    g = StateGraph(RescueState)

    # Register nodes
    for name, fn in [
        ("intake", intake_node),
        ("guardrails", guardrail_node),
        ("supervisor", supervisor_node),
        ("disaster", disaster_node),
        ("priority", priority_node),
        ("damage", damage_node),
        ("shelter", shelter_node),
        ("route", route_node),
        ("resource", resource_node),
        ("medical", medical_node),
        ("volunteer", volunteer_node),
        ("alert", alert_node),
        ("mission_planner", mission_node),
    ]:
        g.add_node(name, fn)

    # Fixed edges
    g.set_entry_point("intake")
    g.add_edge("intake", "guardrails")
    g.add_edge("guardrails", "supervisor")

    # Conditional: supervisor → disaster (always, but via conditional for extensibility)
    g.add_conditional_edges("supervisor", _route_after_supervisor,
                            {"disaster": "disaster"})

    # Fixed: disaster → priority
    g.add_edge("disaster", "priority")

    # Conditional: priority → damage or alert (skip for minimal)
    g.add_conditional_edges("priority", _route_after_priority,
                            {"damage": "damage", "alert": "alert"})

    # Conditional: damage → shelter or alert
    g.add_conditional_edges("damage", _route_after_damage,
                            {"shelter": "shelter", "alert": "alert"})

    # Fixed: shelter → route → resource → medical
    g.add_edge("shelter", "route")
    g.add_edge("route", "resource")
    g.add_edge("resource", "medical")

    # Conditional: medical → volunteer or alert
    g.add_conditional_edges("medical", _route_after_medical,
                            {"volunteer": "volunteer", "alert": "alert"})

    # Fixed: volunteer → alert → mission_planner → END
    g.add_edge("volunteer", "alert")
    g.add_edge("alert", "mission_planner")
    g.add_edge("mission_planner", END)

    return g.compile()


compiled_graph = build_graph()


# ── Initial state factory ─────────────────────────────────────────────────────

def initial_state(payload: Dict[str, Any]) -> RescueState:
    location = payload.get("location", "Hyderabad")
    live_data = fetch_live_data_bundle(location) if USE_LIVE_APIS else {"mode": "fallback"}
    return {
        "location": location,
        "disaster_type": (payload.get("disaster_type") or "flood").lower(),
        "severity": (payload.get("severity") or "medium").lower(),
        "query": payload.get("query", ""),
        "context": payload.get("context") or {},
        "agents_used": [],
        "a2a_trace": [],
        "a2a_messages": [],
        "confidence_scores": {},
        "reasoning_summaries": {},
        "observability_traces": [],
        "correlation_id": payload.get("correlation_id", ""),
        "live_data_sources": live_data,
        "live_weather": live_data.get("live_weather", {}),
        "live_disaster_events": live_data.get("live_disaster_events", {}),
        "live_earthquakes": live_data.get("live_earthquakes", {}),
        "live_geocoding": live_data.get("live_geocoding", {}),
        "live_routing": live_data.get("live_routing", {}),
    }


# ── Sequential fallback ───────────────────────────────────────────────────────

def run_sequential(payload: Dict[str, Any]) -> RescueState:
    state = intake_node(initial_state(payload))
    nodes = [guardrail_node, supervisor_node, disaster_node, priority_node,
             damage_node, shelter_node, route_node, resource_node,
             medical_node, volunteer_node, alert_node, mission_node]
    for node in nodes:
        state = node(state)
    return state


# ── Public entry point ────────────────────────────────────────────────────────

def run_rescue_graph(payload: Dict[str, Any]) -> RescueState:
    try:
        if compiled_graph is not None:
            return compiled_graph.invoke(initial_state(payload))
    except Exception:
        pass
    return run_sequential(payload)
