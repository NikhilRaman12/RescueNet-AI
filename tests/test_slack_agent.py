from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_slack_status_endpoint():
    response = client.get("/api/slack/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert "/rescuenet" == body["slash_command"]
    assert "get_weather_alert" in body["mcp_tools"]


def test_slack_analyze_returns_blockkit_card():
    response = client.post(
        "/api/slack/analyze",
        json={
            "text": "Flood water crossed bridge near Village A. 70 people stranded, elderly and children present.",
            "channel": "field-reports",
            "user_id": "U-demo",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending_human_approval"
    assert body["card"]["risk"]["score"] >= 70
    assert body["slack_message"]["blocks"]
    assert body["card"]["safety"]["human_approval_required"] is True


def test_slack_command_demo_and_action_flow():
    command_response = client.post("/api/slack/command", json={"text": "demo", "channel": "incident-command", "user_id": "U-demo"})
    assert command_response.status_code == 200
    command_body = command_response.json()
    incident_id = command_body["card"]["incident"]["incident_id"]

    action_response = client.post(
        "/api/slack/actions",
        json={"action_id": "approve_response_plan", "incident_id": incident_id, "user_id": "U-commander"},
    )
    assert action_response.status_code == 200
    assert action_response.json()["status"] == "approved"
