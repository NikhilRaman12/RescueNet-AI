from __future__ import annotations

from typing import Any, Dict, List

from rescuenet_slack.incident_models import IncidentExtraction, RiskAssessment, _priority_tier


# Deterministic scoring weights — LLM may explain but never decides the score
_WEIGHTS = {
    "people_affected": 20,       # max 20
    "vulnerable_groups": 15,     # max 15
    "medical_urgency": 12,       # max 12
    "hazard_severity": 15,       # max 15
    "escalation_trend": 10,      # max 10
    "access_constraints": 15,    # max 15
    "resource_gap": 13,          # max 13
}
# Total max = 100


def score_incident(incident: IncidentExtraction, context: Dict[str, Any]) -> RiskAssessment:
    breakdown: Dict[str, int] = {}
    factors: List[str] = []

    # 1. People affected (max 20)
    if incident.people_affected >= 100:
        breakdown["people_affected"] = 20
        factors.append("mass casualty scale (100+ people)")
    elif incident.people_affected >= 50:
        breakdown["people_affected"] = 16
        factors.append("large affected population (50+)")
    elif incident.people_affected >= 20:
        breakdown["people_affected"] = 10
        factors.append("significant affected population (20+)")
    elif incident.people_affected >= 5:
        breakdown["people_affected"] = 5
        factors.append("multiple people affected")
    else:
        breakdown["people_affected"] = 0

    # 2. Vulnerable groups (max 15)
    vg_count = len(incident.vulnerable_groups)
    if vg_count >= 2:
        breakdown["vulnerable_groups"] = 15
        factors.append(f"multiple vulnerable groups: {', '.join(incident.vulnerable_groups)}")
    elif vg_count == 1:
        breakdown["vulnerable_groups"] = 9
        factors.append(f"vulnerable group present: {incident.vulnerable_groups[0]}")
    else:
        breakdown["vulnerable_groups"] = 0

    # 3. Medical urgency (max 12)
    if incident.medical_urgency:
        breakdown["medical_urgency"] = 12
        factors.append("medical urgency reported")
    else:
        breakdown["medical_urgency"] = 0

    # 4. Hazard severity from weather/hazard type (max 15)
    weather = context.get("weather_alert") or {}
    weather_risk = str(weather.get("risk", "")).lower()
    hazard = incident.hazard_type.lower()
    if weather_risk in {"critical", "very_high"} or hazard in {"earthquake", "cyclone"}:
        breakdown["hazard_severity"] = 15
        factors.append("critical hazard conditions")
    elif weather_risk == "high" or hazard in {"flood", "wildfire"}:
        breakdown["hazard_severity"] = 10
        factors.append("high hazard severity")
    elif weather_risk == "moderate":
        breakdown["hazard_severity"] = 5
        factors.append("moderate hazard conditions")
    else:
        breakdown["hazard_severity"] = 3

    # 5. Escalation trend from Slack context (max 10)
    slack_ctx = context.get("slack_context") or {}
    related = slack_ctx.get("related_threads", {})
    thread_count = related.get("count", 0)
    if thread_count >= 4:
        breakdown["escalation_trend"] = 10
        factors.append("multiple corroborating field reports")
    elif thread_count >= 2:
        breakdown["escalation_trend"] = 6
        factors.append("corroborating reports in Slack context")
    elif thread_count >= 1:
        breakdown["escalation_trend"] = 3
        factors.append("at least one related Slack thread found")
    else:
        breakdown["escalation_trend"] = 0

    # 6. Access constraints from route risk (max 15)
    route = context.get("route_risk") or {}
    route_risk = str(route.get("risk_level", "")).lower()
    blocked = route.get("blocked_routes", [])
    if route_risk in {"critical", "high"} and blocked:
        breakdown["access_constraints"] = 15
        factors.append(f"route access blocked: {', '.join(blocked[:2])}")
    elif route_risk in {"critical", "high"}:
        breakdown["access_constraints"] = 10
        factors.append("high route risk reported")
    elif route_risk == "moderate":
        breakdown["access_constraints"] = 5
        factors.append("moderate access constraints")
    else:
        breakdown["access_constraints"] = 0

    # 7. Resource gap (max 13)
    resources = context.get("available_resources") or {}
    shortages = resources.get("shortages", [])
    shelter = context.get("shelter_capacity") or {}
    available_spaces = shelter.get("available_spaces", 999)
    if shortages and available_spaces < incident.people_affected:
        breakdown["resource_gap"] = 13
        factors.append(f"resource shortages and shelter capacity gap: {', '.join(shortages[:3])}")
    elif shortages:
        breakdown["resource_gap"] = 8
        factors.append(f"resource shortages: {', '.join(shortages[:3])}")
    elif available_spaces < incident.people_affected:
        breakdown["resource_gap"] = 6
        factors.append("shelter capacity may be insufficient")
    else:
        breakdown["resource_gap"] = 0

    score = min(100, max(0, sum(breakdown.values())))
    tier = _priority_tier(score)
    level = tier.lower() if tier != "SEVERE" else "high"
    # Map tiers to legacy level strings for backward compat
    level_map = {"LOW": "watch", "MODERATE": "moderate", "HIGH": "high", "SEVERE": "high", "CRITICAL": "critical"}
    level = level_map[tier]

    confidence = round(0.65 + min(0.30, len(factors) * 0.04), 2)

    return RiskAssessment(
        score=score,
        level=level,
        priority_tier=tier,
        confidence=confidence,
        factors=factors or ["limited context — verify field reports"],
        scoring_breakdown=breakdown,
    )
