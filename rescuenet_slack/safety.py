from __future__ import annotations

from typing import Any, Dict, List

from rescuenet_slack.incident_models import SafetyReview


def review_plan(context: Dict[str, Any], confidence: float) -> SafetyReview:
    sources: List[str] = ["slack_context_search", "rescuenet_multi_agent_graph", "mcp_tool_layer"]
    unsupported_claims: List[str] = []

    if not context.get("available_resources"):
        unsupported_claims.append("Resource availability needs confirmation before dispatch.")
    if not context.get("shelter_capacity"):
        unsupported_claims.append("Shelter capacity needs confirmation before routing evacuees.")

    return SafetyReview(
        human_approval_required=True,
        confidence=round(max(0.0, min(1.0, confidence)), 2),
        data_sources=sources,
        unsupported_claims=unsupported_claims,
    )

