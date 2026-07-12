import os
from fastapi.testclient import TestClient
from backend.main import app
from rescuenet_slack.store import get_incident, get_response_plan, get_evidence

client = TestClient(app)

def test_live_disaster_vertical_flow():
    # Force USE_LIVE_APIS to True for this flow
    os.environ["USE_LIVE_APIS"] = "true"
    
    # 1. Analyze field report
    report_text = "Flood near Vijayawada. 120 people trapped, need immediate boat dispatch and shelter backup."
    resp = client.post(
        "/api/slack/analyze",
        json={
            "text": report_text,
            "channel": "field-reports",
            "user_id": "U-field-responder",
            "location": "Vijayawada",
            "hazard_type": "flood"
        }
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "pending_human_approval"
    
    card = body["card"]
    incident_id = card["incident"]["incident_id"]
    
    assert card["incident"]["location"] == "Vijayawada"
    assert card["incident"]["hazard_type"] == "flood"
    assert card["risk"]["score"] > 50
    
    # Assert live APIs were queried
    sources = card["safety"]["data_sources"]
    assert any("live" in s.lower() or "open-meteo" in s.lower() or "osrm" in s.lower() for s in sources)

    # 2. Verify persisted in SQLite
    incident = get_incident(incident_id)
    assert incident is not None
    assert incident["approval_status"] == "pending_human_approval"
    
    plan = get_response_plan(incident_id)
    assert plan is not None
    assert len(plan["actions"]) > 0
    
    evidence = get_evidence(incident_id)
    assert len(evidence) > 0

    # 3. Simulate human approval interaction
    action_resp = client.post(
        "/api/slack/actions",
        json={
            "action_id": "approve_response_plan",
            "incident_id": incident_id,
            "user_id": "U-commander"
        }
    )
    assert action_resp.status_code == 200
    assert action_resp.json()["status"] == "approved"
    
    # 4. Verify status updated in database
    updated_incident = get_incident(incident_id)
    assert updated_incident["approval_status"] == "approved"

    # 5. Verify A2A messages ledger was populated
    ledger_resp = client.get("/api/a2a/messages")
    assert ledger_resp.status_code == 200
    ledger_body = ledger_resp.json()
    assert ledger_body["count"] > 0
    assert any(m["sender_agent"] == "Disaster Intelligence Agent" for m in ledger_body["messages"])
