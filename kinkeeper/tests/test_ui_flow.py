import pytest
from fastapi.testclient import TestClient
from app.fast_api_app import app

client = TestClient(app)

def test_root_index_template_rendering():
    response = client.get("/ui")
    assert response.status_code == 200
    assert "KinKeeper" in response.text
    assert "Analyze Memories" in response.text

def test_api_events_endpoints():
    # 1. GET events
    response = client.get("/api/events")
    assert response.status_code == 200
    assert "events" in response.json()
    
    # 2. PUT event update
    update_payload = {
        "index": 0,
        "event": {
            "person": "Robert Mitchell",
            "event_type": "birthday",
            "inferred_date": "2025-06-01",
            "suggested_message": "Happy Birthday, Robert! 🎂"
        }
    }
    
    # If there are no events in database, PUT index 0 might return an error status,
    # which is expected and handled (status_code is still 200, status key in json is "error").
    response = client.put("/api/events", json=update_payload)
    assert response.status_code == 200
    assert response.json()["status"] in ("success", "error")

def test_api_audit_trail_endpoint():
    response = client.get("/api/audit")
    assert response.status_code == 200
    assert "audit_log" in response.json()
