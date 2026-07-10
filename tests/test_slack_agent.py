from fastapi.testclient import TestClient

from backend.main import app
from rescuenet_slack.incident_models import IncidentExtraction, _priority_tier
from rescuenet_slack.risk_engine import score_incident
from slack_app.blockkit import help_message, incident_report_modal

client = TestClient(app)

DEMO_TEXT = (
    "Flood water has crossed the bridge near Village A. "
    "Around 70 people are stranded, including elderly residents and children. "
    "Main road may be blocked."
)


# ── Priority tier mapping ────────────────────────────────────────────────────

def test_priority_tier_critical():
    assert _priority_tier(90) == "CRITICAL"

def test_priority_tier_severe():
    assert _priority_tier(75) == "SEVERE"

def test_priority_tier_high():
    assert _priority_tier(55) == "HIGH"

def test_priority_tier_moderate():
    assert _priority_tier(35) == "MODERATE"

def test_priority_tier_low():
    assert _priority_tier(10) == "LOW"


# ── Deterministic risk scoring ───────────────────────────────────────────────

def test_risk_score_village_a_flood():
    incident = IncidentExtraction(
        location="Village A",
        hazard_type="flood",
        people_affected=70,
        vulnerable_groups=["elderly", "children"],
        urgency="critical",
        medical_urgency=False,
    )
    context = {
        "weather_alert": {"risk": "high"},
        "route_risk": {"risk_level": "high", "blocked_routes": ["old bridge road"]},
        "available_resources": {"shortages": ["water"]},
        "shelter_capacity": {"available_spaces": 50},
        "slack_context": {"related_threads": {"count": 3}},
    }
    risk = score_incident(incident, context)
    assert risk.score >= 70
    assert risk.priority_tier in {"SEVERE", "CRITICAL"}
    assert risk.scoring_breakdown
    assert risk.factors
    # LLM must not decide score — breakdown must sum to score
    assert sum(risk.scoring_breakdown.values()) == risk.score


def test_risk_score_low_incident():
    incident = IncidentExtraction(
        location="Village B",
        hazard_type="field emergency",
        people_affected=2,
        vulnerable_groups=[],
        urgency="medium",
        medical_urgency=False,
    )
    risk = score_incident(incident, {})
    assert risk.score < 50
    assert risk.priority_tier in {"LOW", "MODERATE"}


def test_risk_score_all_seven_factors_present():
    incident = IncidentExtraction(
        location="Village A",
        hazard_type="flood",
        people_affected=70,
        vulnerable_groups=["elderly", "children"],
        urgency="critical",
        medical_urgency=True,
    )
    context = {
        "weather_alert": {"risk": "high"},
        "route_risk": {"risk_level": "high", "blocked_routes": ["bridge road"]},
        "available_resources": {"shortages": ["water", "boats"]},
        "shelter_capacity": {"available_spaces": 30},
        "slack_context": {"related_threads": {"count": 5}},
    }
    risk = score_incident(incident, context)
    keys = set(risk.scoring_breakdown.keys())
    assert keys == {"people_affected", "vulnerable_groups", "medical_urgency",
                    "hazard_severity", "escalation_trend", "access_constraints", "resource_gap"}


# ── Slack API endpoints ──────────────────────────────────────────────────────

def test_slack_status_endpoint():
    resp = client.get("/api/slack/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ready"
    assert body["slash_command"] == "/rescuenet"
    assert "get_weather_alert" in body["mcp_tools"]


def test_slack_events_route_reports_missing_credentials():
    status = client.get("/slack/events")
    assert status.status_code == 200
    assert status.json()["configured"] is False

    resp = client.post("/slack/events", json={"type": "url_verification", "challenge": "demo"})
    assert resp.status_code == 503
    assert "SLACK_BOT_TOKEN" in resp.json()["detail"]


def test_slack_analyze_returns_blockkit_card():
    resp = client.post(
        "/api/slack/analyze",
        json={"text": DEMO_TEXT, "channel": "field-reports", "user_id": "U-demo"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "pending_human_approval"
    assert body["card"]["risk"]["score"] >= 70
    assert body["card"]["risk"]["priority_tier"] in {"SEVERE", "CRITICAL"}
    assert body["slack_message"]["blocks"]
    assert body["card"]["safety"]["human_approval_required"] is True


def test_slack_analyze_score_breakdown_present():
    resp = client.post(
        "/api/slack/analyze",
        json={"text": DEMO_TEXT, "channel": "field-reports", "user_id": "U-demo"},
    )
    breakdown = resp.json()["card"]["risk"]["scoring_breakdown"]
    assert isinstance(breakdown, dict)
    assert len(breakdown) == 7


# ── All slash commands ───────────────────────────────────────────────────────

def test_command_help():
    resp = client.post("/api/slack/command", json={"text": "help", "channel": "incident-command", "user_id": "U-demo"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["response_type"] == "ephemeral"
    assert "blocks" in body
    # Must list all 7 commands
    text = str(body["blocks"])
    for cmd in ["help", "demo", "analyze", "status", "incidents", "resources", "plan"]:
        assert cmd in text


def test_command_status():
    resp = client.post("/api/slack/command", json={"text": "status", "channel": "incident-command", "user_id": "U-demo"})
    assert resp.status_code == 200
    assert resp.json()["response_type"] == "ephemeral"
    assert "MCP tools" in resp.json()["text"]


def test_command_demo():
    resp = client.post("/api/slack/command", json={"text": "demo", "channel": "incident-command", "user_id": "U-demo"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["response_type"] == "in_channel"
    assert body["card"]["incident"]["location"] == "Village A"
    assert body["card"]["incident"]["hazard_type"] == "flood"
    assert body["card"]["incident"]["people_affected"] == 70


def test_command_analyze():
    resp = client.post("/api/slack/command", json={"text": 'analyze "Bridge flooded near Town B. 30 people trapped."', "channel": "field-reports", "user_id": "U-demo"})
    assert resp.status_code == 200
    assert resp.json()["response_type"] == "in_channel"


def test_command_incidents_after_demo():
    # Seed an incident
    client.post("/api/slack/command", json={"text": "demo", "channel": "incident-command", "user_id": "U-demo"})
    resp = client.post("/api/slack/command", json={"text": "incidents", "channel": "incident-command", "user_id": "U-demo"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["response_type"] == "ephemeral"
    assert "incident-" in body["text"]


def test_command_resources():
    resp = client.post("/api/slack/command", json={"text": "resources Village A", "channel": "incident-command", "user_id": "U-demo"})
    assert resp.status_code == 200
    assert resp.json()["response_type"] == "ephemeral"
    assert "Village A" in resp.json()["text"]


def test_command_plan_after_demo():
    demo_resp = client.post("/api/slack/command", json={"text": "demo", "channel": "incident-command", "user_id": "U-demo"})
    incident_id = demo_resp.json()["card"]["incident"]["incident_id"]
    resp = client.post("/api/slack/command", json={"text": f"plan {incident_id}", "channel": "incident-command", "user_id": "U-demo"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["response_type"] == "ephemeral"
    assert incident_id in body["text"]
    assert "Actions" in body["text"]


# ── Block Kit card structure ─────────────────────────────────────────────────

def test_blockkit_has_all_five_buttons():
    resp = client.post("/api/slack/analyze", json={"text": DEMO_TEXT, "channel": "field-reports", "user_id": "U-demo"})
    blocks = resp.json()["slack_message"]["blocks"]
    action_block = next(b for b in blocks if b["type"] == "actions")
    action_ids = [e["action_id"] for e in action_block["elements"]]
    assert "approve_response_plan" in action_ids
    assert "request_revision" in action_ids
    assert "escalate_to_commander" in action_ids
    assert "view_evidence" in action_ids
    assert "refresh_context" in action_ids


def test_blockkit_header_contains_priority_tier():
    resp = client.post("/api/slack/analyze", json={"text": DEMO_TEXT, "channel": "field-reports", "user_id": "U-demo"})
    blocks = resp.json()["slack_message"]["blocks"]
    header_text = blocks[0]["text"]["text"]
    assert "Priority" in header_text
    assert any(tier in header_text for tier in ["CRITICAL", "SEVERE", "HIGH", "MODERATE", "LOW"])


def test_blockkit_metadata_has_incident_id():
    resp = client.post("/api/slack/analyze", json={"text": DEMO_TEXT, "channel": "field-reports", "user_id": "U-demo"})
    meta = resp.json()["slack_message"]["metadata"]["event_payload"]
    assert "incident_id" in meta
    assert "priority_tier" in meta


def test_help_message_structure():
    msg = help_message()
    assert msg["response_type"] == "ephemeral"
    assert msg["blocks"]


def test_incident_report_modal_structure():
    modal = incident_report_modal("C-demo")
    assert modal["type"] == "modal"
    assert modal["callback_id"] == "incident_report_submit"
    assert modal["private_metadata"] == "C-demo"
    block_ids = [block["block_id"] for block in modal["blocks"] if "block_id" in block]
    assert "field_report" in block_ids
    assert "location" in block_ids
    assert "hazard_type" in block_ids


# ── Human approval workflow ──────────────────────────────────────────────────

def test_full_approval_workflow():
    # 1. Create incident
    cmd_resp = client.post("/api/slack/command", json={"text": "demo", "channel": "incident-command", "user_id": "U-demo"})
    incident_id = cmd_resp.json()["card"]["incident"]["incident_id"]

    # 2. Approve
    action_resp = client.post("/api/slack/actions", json={"action_id": "approve_response_plan", "incident_id": incident_id, "user_id": "U-commander"})
    assert action_resp.status_code == 200
    assert action_resp.json()["status"] == "approved"

    # 3. Verify store updated
    detail = client.get(f"/api/incidents/{incident_id}").json()
    assert detail["incident"]["approval_status"] == "approved"


def test_revision_workflow():
    cmd_resp = client.post("/api/slack/command", json={"text": "demo", "channel": "incident-command", "user_id": "U-demo"})
    incident_id = cmd_resp.json()["card"]["incident"]["incident_id"]
    resp = client.post("/api/slack/actions", json={"action_id": "request_revision", "incident_id": incident_id, "user_id": "U-commander"})
    assert resp.json()["status"] == "revision_requested"


def test_escalation_workflow():
    cmd_resp = client.post("/api/slack/command", json={"text": "demo", "channel": "incident-command", "user_id": "U-demo"})
    incident_id = cmd_resp.json()["card"]["incident"]["incident_id"]
    resp = client.post("/api/slack/actions", json={"action_id": "escalate_to_commander", "incident_id": incident_id, "user_id": "U-commander"})
    assert resp.json()["status"] == "escalated"


# ── Store persistence ────────────────────────────────────────────────────────

def test_incident_persisted_to_store():
    resp = client.post("/api/slack/analyze", json={"text": DEMO_TEXT, "channel": "field-reports", "user_id": "U-demo"})
    incident_id = resp.json()["card"]["incident"]["incident_id"]

    detail = client.get(f"/api/incidents/{incident_id}").json()
    assert detail["incident"]["incident_id"] == incident_id
    assert detail["plan"] is not None
    assert isinstance(detail["evidence"], list)
    assert len(detail["evidence"]) >= 2  # slack_context + mcp_context
    assert isinstance(detail["audit"], list)
    assert len(detail["audit"]) >= 2  # incident_detected + response_plan_generated


def test_list_incidents_endpoint():
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    assert isinstance(resp.json()["incidents"], list)


def test_audit_endpoint():
    resp = client.get("/api/audit")
    assert resp.status_code == 200
    assert isinstance(resp.json()["audit"], list)


def test_dashboard_endpoint():
    resp = client.get("/api/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_incidents" in body
    assert "critical_incidents" in body
    assert "pending_approvals" in body


# ── MCP demo tools ───────────────────────────────────────────────────────────

def test_mcp_context_has_all_tools():
    resp = client.get("/api/slack/mcp/context?location=Village+A")
    assert resp.status_code == 200
    body = resp.json()
    assert "weather_alert" in body
    assert "shelter_capacity" in body
    assert "available_resources" in body
    assert "hospital_status" in body
    assert "route_risk" in body


def test_mcp_weather_is_labeled_demo():
    resp = client.get("/api/slack/mcp/context?location=Village+A")
    weather = resp.json()["weather_alert"]
    assert weather["tool"] == "get_weather_alert"
    # Must not claim to be live
    assert weather.get("source") != "live"


# ── Context search adapter ───────────────────────────────────────────────────

def test_context_search_returns_village_a_messages():
    from slack_app.context_search import build_slack_context
    ctx = build_slack_context("Village A", "flood")
    assert "related_threads" in ctx
    assert "resource_mentions" in ctx
    assert "latest_field_reports" in ctx
    assert ctx["related_threads"]["count"] >= 1


def test_context_search_mode_is_mock():
    from slack_app.context_search import search_slack_context
    result = search_slack_context("flood Village A")
    assert result["mode"] == "mock_rts_search"
