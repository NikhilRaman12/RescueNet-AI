from __future__ import annotations

from rescuenet_slack.store import (
    get_audit_trail,
    get_evidence,
    get_incident,
    get_response_plan,
    list_incidents,
    record_approval,
    record_audit,
    save_evidence,
    save_response_plan,
    upsert_incident,
)


def _sample(suffix: str = "test") -> dict:
    return {
        "incident_id": f"incident-store-{suffix}",
        "location": "Village A",
        "hazard_type": "flood",
        "people_affected": 70,
        "vulnerable_groups": ["elderly", "children"],
        "urgency": "critical",
        "risk_score": 82,
        "risk_level": "high",
        "priority_tier": "SEVERE",
        "approval_status": "pending_human_approval",
        "source_channel": "field-reports",
        "source_text": "Flood near Village A.",
        "detected_at": "2026-07-07T09:10:00+00:00",
    }


def test_upsert_and_get_incident():
    data = _sample("upsert")
    upsert_incident(data)
    result = get_incident(data["incident_id"])
    assert result is not None
    assert result["location"] == "Village A"
    assert result["priority_tier"] == "SEVERE"
    assert isinstance(result["vulnerable_groups"], list)


def test_update_approval_via_record_approval():
    data = _sample("approval")
    upsert_incident(data)
    record_approval(data["incident_id"], "approved", "U-commander")
    result = get_incident(data["incident_id"])
    assert result["approval_status"] == "approved"


def test_save_and_get_response_plan():
    data = _sample("plan")
    upsert_incident(data)
    plan = {
        "summary": "High priority flood response.",
        "actions": ["Dispatch boat team", "Open shelter C"],
        "resources": ["Boat Team 2: available"],
        "follow_up_minutes": 15,
    }
    save_response_plan(data["incident_id"], plan)
    result = get_response_plan(data["incident_id"])
    assert result is not None
    assert result["summary"] == plan["summary"]
    assert "Dispatch boat team" in result["actions"]


def test_save_and_get_evidence():
    data = _sample("evidence")
    upsert_incident(data)
    save_evidence(data["incident_id"], "slack_context", {"count": 3})
    save_evidence(data["incident_id"], "mcp_context", {"weather": "high"})
    evidence = get_evidence(data["incident_id"])
    assert len(evidence) >= 2
    sources = [e["source"] for e in evidence]
    assert "slack_context" in sources
    assert "mcp_context" in sources


def test_record_and_get_audit():
    data = _sample("audit")
    upsert_incident(data)
    record_audit(data["incident_id"], "incident_detected", "U-demo", {"channel": "field-reports"})
    record_audit(data["incident_id"], "approved", "U-commander", {})
    trail = get_audit_trail(data["incident_id"])
    actions = [a["action"] for a in trail]
    assert "incident_detected" in actions
    assert "approved" in actions


def test_list_incidents_returns_list():
    upsert_incident(_sample("list"))
    rows = list_incidents(50)
    assert isinstance(rows, list)
    assert len(rows) >= 1


def test_upsert_updates_existing():
    data = _sample("update")
    upsert_incident(data)
    data["approval_status"] = "escalated"
    data["risk_score"] = 95
    upsert_incident(data)
    result = get_incident(data["incident_id"])
    assert result["approval_status"] == "escalated"
