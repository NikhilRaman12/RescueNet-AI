from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_rescue_endpoint():
    response = client.post(
        "/api/rescue",
        json={
            "location": "Hyderabad",
            "disaster_type": "flood",
            "severity": "high",
            "query": "Flood alert near river zone. People are trapped and injured. Evacuation is needed.",
            "context": {},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["location"] == "Hyderabad"
    assert body["agents_used"]
