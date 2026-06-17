from typing import TypedDict, Dict, Any, List
from backend.a2a.protocol import a2a_handoff
from backend.services.live_data_tools import fetch_live_data_bundle
from backend.a2a.protocol import a2a_handoff

try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except Exception:
    StateGraph = None
    END = None
    LANGGRAPH_AVAILABLE = False

from backend.agents.disaster_agent import DisasterIntelligenceAgent
from backend.agents.priority_agent import PriorityScoringAgent
from backend.agents.damage_agent import DamageAssessmentAgent
from backend.agents.shelter_agent import ShelterCoordinationAgent
from backend.agents.route_agent import RouteOptimizationAgent
from backend.agents.resource_agent import ResourceAgent
from backend.agents.medical_agent import MedicalTriageAgent
from backend.agents.volunteer_agent import VolunteerCoordinationAgent
from backend.agents.alert_agent import AlertAgent
from backend.agents.mission_agent import MissionPlannerAgent


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
    shelters: List[Dict[str, Any]]
    routes: Dict[str, Any]
    resources: Dict[str, Any]
    resource_priority: List[str]
    medical_triage: Dict[str, Any]
    volunteers: Dict[str, int]
    public_alert: Dict[str, Any]
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


def disaster_node(state: RescueState) -> RescueState:
    state =state = disaster_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Disaster Intelligence Agent",
        "Priority Scoring Agent",
        "Disaster risk assessment completed and transferred for priority scoring",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Disaster Intelligence Agent",
        "Priority Scoring Agent",
        "Disaster risk assessment completed and transferred for priority scoring",
        state.get("risk_level", "medium"),
    )


def priority_node(state: RescueState) -> RescueState:
    state =state = priority_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Priority Scoring Agent",
        "Damage Assessment Agent",
        "Priority score completed and transferred for impact analysis",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Priority Scoring Agent",
        "Damage Assessment Agent",
        "Priority score completed and transferred for impact analysis",
        state.get("risk_level", "medium"),
    )


def damage_node(state: RescueState) -> RescueState:
    state =state = damage_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Damage Assessment Agent",
        "Shelter Coordination Agent",
        "Damage impact estimated and transferred for shelter planning",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Damage Assessment Agent",
        "Shelter Coordination Agent",
        "Damage impact estimated and transferred for shelter planning",
        state.get("risk_level", "medium"),
    )


def shelter_node(state: RescueState) -> RescueState:
    state =state = shelter_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Shelter Coordination Agent",
        "Route Optimization Agent",
        "Shelter capacity mapped and transferred for evacuation routing",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Shelter Coordination Agent",
        "Route Optimization Agent",
        "Shelter capacity mapped and transferred for evacuation routing",
        state.get("risk_level", "medium"),
    )


def route_node(state: RescueState) -> RescueState:
    state =state = route_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Route Optimization Agent",
        "Resource Allocation Agent",
        "Evacuation route intelligence completed and transferred for resource allocation",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Route Optimization Agent",
        "Resource Allocation Agent",
        "Evacuation route intelligence completed and transferred for resource allocation",
        state.get("risk_level", "medium"),
    )


def resource_node(state: RescueState) -> RescueState:
    state =state = resource_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Resource Allocation Agent",
        "Medical Triage Agent",
        "Resource plan completed and transferred for medical triage",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Resource Allocation Agent",
        "Medical Triage Agent",
        "Resource plan completed and transferred for medical triage",
        state.get("risk_level", "medium"),
    )


def medical_node(state: RescueState) -> RescueState:
    state =state = medical_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Medical Triage Agent",
        "Volunteer Coordination Agent",
        "Medical triage plan completed and transferred for volunteer assignment",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Medical Triage Agent",
        "Volunteer Coordination Agent",
        "Medical triage plan completed and transferred for volunteer assignment",
        state.get("risk_level", "medium"),
    )


def volunteer_node(state: RescueState) -> RescueState:
    state =state = volunteer_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Volunteer Coordination Agent",
        "Public Alert Agent",
        "Volunteer squads assigned and transferred for public communication",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Volunteer Coordination Agent",
        "Public Alert Agent",
        "Volunteer squads assigned and transferred for public communication",
        state.get("risk_level", "medium"),
    )


def alert_node(state: RescueState) -> RescueState:
    state =state = alert_agent.run(dict(state))
    return a2a_handoff(
        state,
        "Public Alert Agent",
        "Mission Planner Agent",
        "Public warning generated and transferred for final mission planning",
        state.get("risk_level", "medium"),
    )
    return a2a_handoff(
        state,
        "Public Alert Agent",
        "Mission Planner Agent",
        "Public warning generated and transferred for final mission planning",
        state.get("risk_level", "medium"),
    )


def mission_node(state: RescueState) -> RescueState:
    return mission_agent.run(dict(state))


def initial_state(payload: Dict[str, Any]) -> RescueState:
    location = payload.get("location", "Hyderabad")
    live_data = fetch_live_data_bundle(location)

    return {
        "location": location,
        "disaster_type": payload.get("disaster_type", "flood").lower(),
        "severity": payload.get("severity", "medium").lower(),
        "query": payload.get("query", ""),
        "agents_used": [],
        "a2a_trace": [],
        "correlation_id": payload.get("correlation_id", ""),
        "live_data_sources": live_data,
        "live_weather": live_data.get("live_weather", {}),
        "live_disaster_events": live_data.get("live_disaster_events", {}),
        "live_earthquakes": live_data.get("live_earthquakes", {}),
        "live_geocoding": live_data.get("live_geocoding", {}),
        "live_routing": live_data.get("live_routing", {}),
    }


def run_sequential(payload: Dict[str, Any]) -> RescueState:
    state = initial_state(payload)

    for node in [
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
    graph = StateGraph(RescueState)

    graph.add_node("disaster_intelligence", disaster_node)
    graph.add_node("priority_scoring", priority_node)
    graph.add_node("damage_assessment", damage_node)
    graph.add_node("shelter_coordination", shelter_node)
    graph.add_node("route_optimization", route_node)
    graph.add_node("resource_allocation", resource_node)
    graph.add_node("medical_triage", medical_node)
    graph.add_node("volunteer_coordination", volunteer_node)
    graph.add_node("public_alert", alert_node)
    graph.add_node("mission_planning", mission_node)

    graph.set_entry_point("disaster_intelligence")

    graph.add_edge("disaster_intelligence", "priority_scoring")
    graph.add_edge("priority_scoring", "damage_assessment")
    graph.add_edge("damage_assessment", "shelter_coordination")
    graph.add_edge("shelter_coordination", "route_optimization")
    graph.add_edge("route_optimization", "resource_allocation")
    graph.add_edge("resource_allocation", "medical_triage")
    graph.add_edge("medical_triage", "volunteer_coordination")
    graph.add_edge("volunteer_coordination", "public_alert")
    graph.add_edge("public_alert", "mission_planning")
    graph.add_edge("mission_planning", END)

    return graph.compile()


compiled_graph = build_graph() if LANGGRAPH_AVAILABLE else None


def run_rescue_graph(payload: Dict[str, Any]) -> RescueState:
    if compiled_graph:
        return compiled_graph.invoke(initial_state(payload))
    return run_sequential(payload)
