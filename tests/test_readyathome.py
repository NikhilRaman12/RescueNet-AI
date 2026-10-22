from fastapi.testclient import TestClient

from backend.main import app
from readyathome.service import DEMO_UTTERANCE, build_readiness_plan
from rescuenet_slack.store import get_audit_trail


client = TestClient(app)


def test_readiness_plan_is_deterministic_and_explicitly_simulated():
    first = build_readiness_plan(DEMO_UTTERANCE)
    second = build_readiness_plan(DEMO_UTTERANCE)

    assert first.model_dump() == second.model_dump()
    assert first.intent == "flood_preparedness"
    assert first.experience_label == "Independent Alexa+ interaction simulation"
    assert len(first.tasks) == 5
    assert all(task.source_id in {source.id for source in first.sources} for task in first.tasks)
    assert {tool.status for tool in first.tools} >= {"simulated", "not connected", "local"}


def test_demo_plan_route_returns_assumptions_sources_and_limitations():
    response = client.get("/api/readiness/demo")

    assert response.status_code == 200
    body = response.json()
    assert body["scenario_id"] == "readyathome-flood-demo"
    assert "fictional preparedness rehearsal" in body["assumptions"][0]
    assert "not a forecast" in body["assessment"]["summary"]
    assert any(
        "weather" in item["name"].lower()
        for item in body["tools"]
        if item["status"] == "not connected"
    )
    assert body["tasks"][0]["id"] == "check-official-alerts"


def test_plan_route_recognizes_supported_flood_request():
    response = client.post(
        "/api/readiness/plan",
        json={"utterance": "Alexa, could you help us get ready for heavy rain?"},
    )

    assert response.status_code == 200
    assert response.json()["intent"] == "flood_preparedness"


def test_plan_route_rejects_unsupported_request():
    response = client.post("/api/readiness/plan", json={"utterance": "Help me plan a birthday party."})

    assert response.status_code == 422
    assert "supports flood or heavy-rain" in response.json()["detail"]


def test_plan_route_bounds_input_length():
    response = client.post("/api/readiness/plan", json={"utterance": "flood " + ("x" * 240)})

    assert response.status_code == 422


def test_plan_route_uses_no_external_network(monkeypatch):
    import requests

    def reject_network(*args, **kwargs):
        raise AssertionError("The ReadyAtHome plan must not call external services.")

    monkeypatch.setattr(requests, "get", reject_network)
    response = client.post("/api/readiness/plan", json={"utterance": DEMO_UTTERANCE})

    assert response.status_code == 200


def test_task_completion_is_audited_without_request_text():
    private_text = "flood at 123 Example Street, my family is home"
    plan_response = client.post("/api/readiness/plan", json={"utterance": private_text})
    task_response = client.post(
        "/api/readiness/tasks/check-official-alerts",
        json={"completed": True},
    )
    reopen_response = client.post(
        "/api/readiness/tasks/check-official-alerts",
        json={"completed": False},
    )
    activity_response = client.get("/api/readiness/activity")

    assert plan_response.status_code == 200
    assert task_response.status_code == 200
    assert task_response.json()["completed"] is True
    assert reopen_response.status_code == 200
    assert reopen_response.json()["completed"] is False
    assert activity_response.status_code == 200
    items = activity_response.json()["items"]
    assert any(item["action"] == "readiness_task_completed" for item in items)
    assert any(item["action"] == "readiness_task_reopened" for item in items)
    assert private_text not in str(items)
    assert all("utterance" not in item for item in items)
    audit_records = get_audit_trail(incident_id="readyathome-flood-demo")
    assert private_text not in str(audit_records)


def test_unknown_task_cannot_write_audit_event():
    response = client.post("/api/readiness/tasks/not-a-task", json={"completed": True})

    assert response.status_code == 404
    assert response.json()["detail"] == "Unknown preparedness task."
