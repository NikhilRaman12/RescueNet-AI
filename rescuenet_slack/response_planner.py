from __future__ import annotations

from typing import Any, Dict, List

from rescuenet_slack.incident_models import IncidentExtraction, ResponsePlan, RiskAssessment


def build_response_plan(incident: IncidentExtraction, risk: RiskAssessment, context: Dict[str, Any]) -> ResponsePlan:
    shelters = context.get("shelter_capacity", {}).get("shelters", [])
    hospitals = context.get("hospital_status", {}).get("hospitals", [])
    resources = context.get("available_resources", {})

    primary_shelter = shelters[0]["name"] if shelters else context.get("shelter_capacity", {}).get("primary_shelter", "nearest verified shelter")
    medical_unit = hospitals[0]["name"] if hospitals else "nearest ambulance unit"
    resource_items: List[str] = []

    for item in resources.get("resources", [])[:4]:
        label = item.get("name") or item.get("type")
        status = item.get("status", "available")
        if label:
            resource_items.append(f"{label}: {status}")

    if not resource_items:
        resource_items = ["Field rescue team: verify availability", f"{primary_shelter}: verify capacity", f"{medical_unit}: standby"]

    actions = [
        "Open an incident thread in #incident-command and keep all decisions attached to the incident card.",
        f"Dispatch the nearest verified field response team toward {incident.location}.",
        f"Route evacuees toward {primary_shelter} after local access is confirmed.",
    ]

    if incident.medical_urgency or incident.vulnerable_groups:
        actions.append(f"Place {medical_unit} on standby and prioritize vulnerable groups.")

    if risk.score >= 85:
        actions.append("Escalate to the incident commander for immediate approval.")
    else:
        actions.append("Reassess field reports and route risk before dispatch.")

    return ResponsePlan(
        summary=f"{risk.level.title()} priority {incident.hazard_type} response for {incident.location}.",
        actions=actions,
        resources=resource_items,
        follow_up_minutes=15 if risk.score >= 85 else 30,
    )

