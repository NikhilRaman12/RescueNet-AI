from datetime import datetime, timezone
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.config.settings import CORS_ORIGINS
from backend.main import app
from readyathome.models import ReadinessRequest
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
    assert response.json()["guidance_region"] == "United States"


@pytest.mark.parametrize(
    "utterance",
    [
        "My house is flooding right now.",
        "My house is on fire right now.",
        "We are trapped by rising floodwater.",
        "Someone is in immediate danger and needs help now.",
        "My father is having a stroke.",
        "I cannot breathe.",
    ],
)
def test_plan_route_returns_emergency_guidance_instead_of_a_checklist(utterance):
    response = client.post("/api/readiness/plan", json={"utterance": utterance})

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "contact your local emergency services now" in detail
    assert "cannot assess conditions or send help" in detail


@pytest.mark.parametrize(
    "utterance",
    [
        "Help me prepare for a storm.",
        "Help me prepare for a hurricane.",
        "Help me prepare for a cyclone.",
        "Help me prepare for monsoon season.",
        "Help me prepare for a thunderstorm.",
        "Help me prepare for a typhoon.",
        "Help me prepare for a tsunami.",
        "Help me prepare for a drought.",
        "Help me prepare for flooding during a hurricane.",
    ],
)
def test_plan_route_rejects_hazards_outside_supported_scope(utterance):
    response = client.post("/api/readiness/plan", json={"utterance": utterance})

    assert response.status_code == 422
    assert "supports flood or heavy-rain preparedness only" in response.json()["detail"]


@pytest.mark.parametrize("utterance", ["", "  ", "a", " a ", 123, None, "flood " + ("x" * 240)])
def test_readiness_request_rejects_invalid_input(utterance):
    with pytest.raises(ValidationError):
        ReadinessRequest.model_validate({"utterance": utterance})


def test_readiness_plan_sources_are_secure_official_us_references():
    plan = build_readiness_plan(DEMO_UTTERANCE)

    assert plan.guidance_region == "United States"
    assert len(plan.sources) == 3
    for source in plan.sources:
        parsed = urlsplit(source.url)
        assert parsed.scheme == "https"
        assert parsed.hostname is not None
        assert parsed.hostname.endswith(".gov")
        assert source.kind == "official_guidance"


def test_cors_allows_local_frontend_and_denies_unknown_origin():
    assert "*" not in CORS_ORIGINS
    for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
        allowed = client.options(
            "/api/readiness/plan",
            headers={"Origin": origin, "Access-Control-Request-Method": "POST"},
        )
        assert allowed.headers.get("access-control-allow-origin") == origin

    denied = client.options(
        "/api/readiness/plan",
        headers={"Origin": "https://example.invalid", "Access-Control-Request-Method": "POST"},
    )
    assert denied.headers.get("access-control-allow-origin") is None


def test_activity_is_utc_latest_first_and_capped_at_thirty_items():
    plan_response = client.post("/api/readiness/plan", json={"utterance": DEMO_UTTERANCE})
    assert plan_response.status_code == 200

    for index in range(32):
        response = client.post(
            "/api/readiness/tasks/check-official-alerts",
            json={"completed": index % 2 == 0},
        )
        assert response.status_code == 200

    items = client.get("/api/readiness/activity").json()["items"]
    assert len(items) == 30
    assert items[0]["action"] == "readiness_task_reopened"
    assert items[1]["action"] == "readiness_task_completed"
    timestamps = [datetime.fromisoformat(item["timestamp"]) for item in items]
    assert all(timestamp.tzinfo == timezone.utc for timestamp in timestamps)


def test_plan_route_rejects_unsupported_request():
    response = client.post("/api/readiness/plan", json={"utterance": "Help me plan a birthday party."})

    assert response.status_code == 422
    assert "does not create plans for other hazards" in response.json()["detail"]


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
