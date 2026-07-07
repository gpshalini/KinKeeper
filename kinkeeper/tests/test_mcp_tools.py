import os
import json
import pytest
from app.mcp_server import (
    read_sample_chat_export,
    save_captured_events,
    list_captured_events,
    write_audit_log,
    is_safe_path
)

def test_is_safe_path():
    assert is_safe_path("data/sample_whatsapp_export.txt") is True
    assert is_safe_path(".env") is False
    assert is_safe_path("data/private/secrets.txt") is False
    assert is_safe_path("../outside.txt") is False

def test_read_sample_chat_export():
    # Test valid read
    res = read_sample_chat_export("data/sample_whatsapp_export.txt")
    assert "content" in res
    assert res["safe_for_demo"] is True

    # Test unsafe path read
    res = read_sample_chat_export(".env")
    assert "error" in res
    assert res["safe_for_demo"] is False

def test_save_and_list_captured_events():
    test_events = [
        {
            "person": "Olivia",
            "event_type": "birthday",
            "inferred_date": "2025-06-01",
            "confidence": "high",
            "source_snippet": "Happy birthday Olivia 🎂",
            "suggested_message": "Happy Birthday Olivia! 🎂"
        }
    ]
    
    save_res = save_captured_events(test_events)
    assert "saved_count" in save_res
    assert save_res["saved_count"] == 1
    
    list_res = list_captured_events()
    assert "events" in list_res
    assert len(list_res["events"]) == 1
    assert list_res["events"][0]["person"] == "Olivia"
    assert list_res["events"][0]["suggested_message"] == "Happy Birthday Olivia! 🎂"

def test_write_audit_log():
    test_entry = {
        "timestamp": "2026-07-06T12:00:00",
        "event": "Test Event",
        "agent": "Test Agent",
        "decision": "test_action"
    }
    
    write_audit_log(test_entry)
    
    # Read audit_log.jsonl and check if the entry exists
    audit_path = "artifacts/audit_log.jsonl"
    assert os.path.exists(audit_path)
    
    found = False
    with open(audit_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                # The MCP server maps "event" to "action" in structured_entry
                if data.get("action") == "Test Event":
                    found = True
                    break
    assert found is True
