from __future__ import annotations

from typing import Any, Dict


def completeness_score(state: Dict[str, Any]) -> float:
    required = ["disaster_analysis", "priority_score", "damage_assessment", "public_alert", "recommended_actions", "final_mission_plan"]
    present = sum(1 for key in required if state.get(key))
    return round(present / len(required), 2)


def tool_usage_score(state: Dict[str, Any]) -> float:
    live_sources = state.get("live_data_sources") or {}
    used = sum(1 for value in live_sources.values() if isinstance(value, dict) and value.get("status") in {"live", "fallback"})
    return round(min(1.0, used / 5), 2)


def safety_score(state: Dict[str, Any]) -> float:
    guardrail_report = state.get("guardrail_report") or {}
    if guardrail_report.get("passed"):
        return 0.95
    return 0.8


def agent_trace_score(state: Dict[str, Any]) -> float:
    traces = state.get("a2a_trace") or []
    return round(min(1.0, len(traces) / 8), 2)


def response_structure_score(state: Dict[str, Any]) -> float:
    required_keys = ["mission_id", "correlation_id", "status", "agents_used", "agent_outputs", "recommended_actions"]
    present = sum(1 for key in required_keys if state.get(key))
    return round(present / len(required_keys), 2)


def evaluate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    scores = {
        "completeness_score": completeness_score(state),
        "tool_usage_score": tool_usage_score(state),
        "safety_score": safety_score(state),
        "agent_trace_score": agent_trace_score(state),
        "response_structure_score": response_structure_score(state),
    }
    final_score = round(sum(scores.values()) / len(scores), 2)
    return {
        "scores": scores,
        "final_score": final_score,
        "summary": "Evaluation completed for decision-support prototype.",
    }
