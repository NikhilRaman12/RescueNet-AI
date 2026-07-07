from __future__ import annotations

import re
from typing import Any, Dict

from backend.services.rescue_graph import run_rescue_graph
from mcp_server.tools import gather_mcp_context, log_incident_action as mcp_log_action
from rescuenet_slack.audit_log import log_incident_action
from rescuenet_slack.incident_models import IncidentExtraction, IncidentSignal, SlackIncidentCard
from rescuenet_slack.response_planner import build_response_plan
from rescuenet_slack.risk_engine import score_incident
from rescuenet_slack.safety import review_plan
from slack_app.context_search import build_slack_context


HAZARD_TERMS = {
    "flood": ["flood", "water", "bridge", "river", "rain"],
    "cyclone": ["cyclone", "storm", "wind"],
    "earthquake": ["earthquake", "tremor", "collapsed"],
    "wildfire": ["fire", "smoke", "wildfire"],
    "medical": ["injured", "ambulance", "medical", "hospital"],
}


def extract_incident(signal: IncidentSignal) -> IncidentExtraction:
    text = signal.text.strip()
    lowered = text.lower()
    hazard = signal.hazard_type or "field emergency"
    for candidate, terms in HAZARD_TERMS.items():
        if any(term in lowered for term in terms):
            hazard = candidate
            break

    location = signal.location
    if not location:
        location_match = re.search(r"\b(?:near|at|in)\s+([A-Z][A-Za-z0-9\s-]{2,40})", text)
        location = location_match.group(1).strip(" .") if location_match else "reported area"

    numbers = [int(value) for value in re.findall(r"\b\d{1,4}\b", text)]
    people_affected = max(numbers) if numbers else 0
    vulnerable_groups = [group for group in ["elderly", "children", "disabled", "pregnant"] if group in lowered]
    medical_urgency = any(term in lowered for term in ["injured", "medical", "ambulance", "bleeding", "critical"])
    urgency = "critical" if any(term in lowered for term in ["stranded", "trapped", "urgent", "critical"]) else "high" if people_affected >= 50 else "medium"

    return IncidentExtraction(
        location=location,
        hazard_type=hazard,
        people_affected=people_affected,
        vulnerable_groups=vulnerable_groups,
        urgency=urgency,
        medical_urgency=medical_urgency,
        source_channel=signal.channel,
        source_user=signal.user_id,
        source_text=text,
    )


def analyze_signal(signal: IncidentSignal) -> SlackIncidentCard:
    incident = extract_incident(signal)
    slack_context = build_slack_context(incident.location, incident.hazard_type)
    mcp_context = gather_mcp_context(incident.location)
    rescuenet_state = run_rescue_graph(
        {
            "location": incident.location,
            "disaster_type": incident.hazard_type,
            "severity": incident.urgency,
            "query": signal.text,
            "context": {"slack": slack_context, "mcp": mcp_context},
        }
    )

    merged_context: Dict[str, Any] = {
        **mcp_context,
        "slack_context": slack_context,
        "rescuenet_priority": rescuenet_state.get("priority_score", {}),
    }
    risk = score_incident(incident, merged_context)
    plan = build_response_plan(incident, risk, merged_context)
    safety = review_plan(merged_context, min(risk.confidence, 0.91))
    audit = [
        log_incident_action(incident.incident_id, "incident_detected", signal.user_id, {"channel": signal.channel}),
        mcp_log_action(incident.incident_id, "response_plan_generated"),
    ]

    return SlackIncidentCard(
        incident=incident,
        risk=risk,
        plan=plan,
        safety=safety,
        audit_trail=audit,
    )


def analyze_text(text: str, channel: str = "field-reports", user_id: str = "demo-user") -> SlackIncidentCard:
    return analyze_signal(IncidentSignal(text=text, channel=channel, user_id=user_id))
