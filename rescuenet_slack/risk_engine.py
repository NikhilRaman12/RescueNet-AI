from __future__ import annotations

from typing import Any, Dict, List

from rescuenet_slack.incident_models import IncidentExtraction, RiskAssessment


def score_incident(incident: IncidentExtraction, context: Dict[str, Any]) -> RiskAssessment:
    score = 25
    factors: List[str] = []

    if incident.people_affected >= 50:
        score += 24
        factors.append("large affected population")
    elif incident.people_affected >= 10:
        score += 14
        factors.append("multiple people affected")

    if incident.vulnerable_groups:
        score += 14
        factors.append("vulnerable groups present")

    if incident.medical_urgency:
        score += 12
        factors.append("medical urgency reported")

    route_risk = (context.get("route_risk") or {}).get("risk_level", "")
    if route_risk.lower() in {"high", "critical"}:
        score += 10
        factors.append("route access is constrained")

    weather = context.get("weather_alert") or {}
    if str(weather.get("risk", "")).lower() in {"high", "critical"}:
        score += 10
        factors.append("hazard conditions are worsening")

    if incident.urgency.lower() in {"high", "critical"}:
        score += 8
        factors.append("high urgency language detected")

    resources = context.get("available_resources") or {}
    if resources.get("shortages"):
        score += 5
        factors.append("resource shortage reported")

    score = min(100, max(0, score))
    level = "critical" if score >= 85 else "high" if score >= 70 else "moderate" if score >= 45 else "watch"
    confidence = 0.72 + min(0.2, len(factors) * 0.025)

    return RiskAssessment(score=score, level=level, confidence=round(confidence, 2), factors=factors or ["limited context available"])

