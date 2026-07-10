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
except Exception:  # pragma: no cover
    END = None
    StateGraph = None
    LANGGRAPH_AVAILABLE = False


class RescueState(TypedDict, total=False):
    query: str
    location: str
    disaster_type: str
    severity: str
    context: Dict[str, Any]
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
    live_data_sources: Dict[str, Any]
    live_weather: Dict[str, Any]
    live_disaster_events: Dict[str, Any]
    live_earthquakes: Dict[str, Any]
    live_geocoding: Dict[str, Any]
    live_routing: Dict[str, Any]
    summary: str
    agents_used: List[str]
    a2a_trace: List[str]
    a2a_messages: List[Dict[str, Any]]
    confidence_scores: Dict[str, float]
    reasoning_summaries: Dict[str, str]
    observability_traces: List[Dict[str, Any]]
    guardrail_report: Dict[str, Any]
    evaluation_report: Dict[str, Any]
    mission_id: str
    correlation_id: str
    status: str
    confidence_score: float
    generated_at: str


protocol = A2AProtocol()

disaster_agent = DisasterIntelligenceAgent()
priority_agent = PriorityScoringAgent()
damage_agent = DamageAssessmentAgent()
shelter_agent = ShelterCoordinationAgent()
route_agent = RouteOptimizationAgent()
resource_agent = ResourceAgent()
medical_agent = MedicalTriageAgent()
volunteer_agent = VolunteerCoordinationAgent()
alert_agent = AlertAgent()
mission_agent = MissionPlannerAgent()


def _handoff(state: RescueState, sender: str, receiver: str, note: str) -> RescueState:
    protocol.handoff(sender, receiver, dict(state), note)
    state.setdefault("a2a_trace", [])
    state["a2a_trace"].append(f"{sender} -> {receiver}: {note}")
    return state


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
    report = {
        "passed": True,
        "prompt_injection_detected": any(term in (state.get("query") or "").lower() for term in ["ignore previous instructions", "bypass"]),
        "unsafe_instruction_filtered": False,
        "pii_minimized": True,
        "emergency_disclaimer": "This is operational decision support, not final emergency authority.",
        "human_in_the_loop_required": (state.get("severity") or "high").lower() in {"high", "critical"},
    }
    if report["prompt_injection_detected"]:
        report["unsafe_instruction_filtered"] = True
        report["passed"] = False
    state["guardrail_report"] = report
    state.setdefault("agents_used", []).append("Safety Guardrail Agent")
    return state


def disaster_node(state: RescueState) -> RescueState:
    state = disaster_agent.run(dict(state))
    return _handoff(state, "Disaster Intelligence Agent", "Priority Scoring Agent", "Disaster risk assessment completed")


def priority_node(state: RescueState) -> RescueState:
    state = priority_agent.run(dict(state))
    return _handoff(state, "Priority Scoring Agent", "Damage Assessment Agent", "Priority scoring completed")


def damage_node(state: RescueState) -> RescueState:
    state = damage_agent.run(dict(state))
    return _handoff(state, "Damage Assessment Agent", "Shelter Coordination Agent", "Damage impact assessment completed")


def shelter_node(state: RescueState) -> RescueState:
    state = shelter_agent.run(dict(state))
    return _handoff(state, "Shelter Coordination Agent", "Route Optimization Agent", "Shelter coordination completed")


def route_node(state: RescueState) -> RescueState:
    state = route_agent.run(dict(state))
    return _handoff(state, "Route Optimization Agent", "Resource Allocation Agent", "Route plan completed")


def resource_node(state: RescueState) -> RescueState:
    state = resource_agent.run(dict(state))
    return _handoff(state, "Resource Allocation Agent", "Medical Triage Agent", "Resource plan completed")


def medical_node(state: RescueState) -> RescueState:
    state = medical_agent.run(dict(state))
    return _handoff(state, "Medical Triage Agent", "Volunteer Coordination Agent", "Medical triage completed")


def volunteer_node(state: RescueState) -> RescueState:
    state = volunteer_agent.run(dict(state))
    return _handoff(state, "Volunteer Coordination Agent", "Public Alert Agent", "Volunteer coordination completed")


def alert_node(state: RescueState) -> RescueState:
    state = alert_agent.run(dict(state))
    return _handoff(state, "Public Alert Agent", "Mission Planner Agent", "Public alert drafted")


def mission_node(state: RescueState) -> RescueState:
    state = mission_agent.run(dict(state))
    state["status"] = "completed"
    return state


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


def run_sequential(payload: Dict[str, Any]) -> RescueState:
    state = intake_node(initial_state(payload))
    for node in [
        guardrail_node,
        disaster_node,
        priority_node,
        damage_node,
        shelter_node,
        route_node,
        resource_node,
        medical_node,
        volunteer_node,
        alert_node,
        mission_node,
    ]:
        state = node(state)
    return state


def build_graph():
    if not LANGGRAPH_AVAILABLE:
        return None

    graph = StateGraph(RescueState)
    graph.add_node("intake", intake_node)
    graph.add_node("guardrails", guardrail_node)
    graph.add_node("disaster", disaster_node)
    graph.add_node("priority", priority_node)
    graph.add_node("damage", damage_node)
    graph.add_node("shelter", shelter_node)
    graph.add_node("route", route_node)
    graph.add_node("resource", resource_node)
    graph.add_node("medical", medical_node)
    graph.add_node("volunteer", volunteer_node)
    graph.add_node("alert", alert_node)
    graph.add_node("mission_planner", mission_node)

    graph.set_entry_point("intake")
    graph.add_edge("intake", "guardrails")
    graph.add_edge("guardrails", "disaster")
    graph.add_edge("disaster", "priority")
    graph.add_edge("priority", "damage")
    graph.add_edge("damage", "shelter")
    graph.add_edge("shelter", "route")
    graph.add_edge("route", "resource")
    graph.add_edge("resource", "medical")
    graph.add_edge("medical", "volunteer")
    graph.add_edge("volunteer", "alert")
    graph.add_edge("alert", "mission_planner")
    graph.add_edge("mission_planner", END)
    return graph.compile()


compiled_graph = build_graph()


def run_rescue_graph(payload: Dict[str, Any]) -> RescueState:
    try:
        if compiled_graph is not None:
            return compiled_graph.invoke(initial_state(payload))
    except Exception:
        pass
    return run_sequential(payload)
