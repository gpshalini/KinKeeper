import os
import re
import json
import datetime
from mcp.server.fastmcp import FastMCP

# Define the FastMCP server
mcp = FastMCP("KinKeeper MCP Server")

ALLOWED_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # kinkeeper root

def is_safe_path(path: str) -> bool:
    abs_path = os.path.abspath(os.path.join(ALLOWED_DIR, path))
    # Must start with project root
    if not abs_path.startswith(ALLOWED_DIR):
        return False
    # Never read .env
    if ".env" in abs_path:
        return False
    # Never read data/private
    private_dir = os.path.abspath(os.path.join(ALLOWED_DIR, "data", "private"))
    if abs_path.startswith(private_dir):
        return False
    # Never read zip/tar archives
    if abs_path.endswith(".zip") or abs_path.endswith(".tar") or abs_path.endswith(".gz"):
        return False
    return True

@mcp.tool()
def read_sample_chat_export(file_path: str) -> dict:
    """Read the synthetic demo file.
    
    Args:
        file_path: The local path of the chat export file to read.
    """
    if not is_safe_path(file_path):
        return {
            "error": "Access denied: Unsafe or forbidden path.",
            "safe_for_demo": False
        }
        
    abs_path = os.path.abspath(os.path.join(ALLOWED_DIR, file_path))
    
    if not os.path.exists(abs_path):
        return {
            "error": f"File not found: {file_path}",
            "safe_for_demo": False
        }
        
    # Check file size (limit to 100 KB for demo safety)
    file_size = os.path.getsize(abs_path)
    if file_size > 100 * 1024:
        return {
            "error": "Access denied: File exceeds maximum allowed size for demo.",
            "safe_for_demo": False
        }
        
    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    return {
        "content": content,
        "source": "synthetic_sample",
        "safe_for_demo": True
    }

@mcp.tool()
def save_captured_events(events: list) -> dict:
    """Save structured captured events to local artifacts.
    
    Args:
        events: List of event dictionaries containing captured details.
    """
    artifacts_dir = os.path.join(ALLOWED_DIR, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    events_path = os.path.join(artifacts_dir, "events.json")
    
    phone_re = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    email_re = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    
    sanitized_events = []
    for ev in events:
        person = ev.get("person", "Unknown person")
        snippet = ev.get("source_snippet", "")
        
        # Double check redaction before committing to disk
        if phone_re.search(person):
            person = "[PHONE_REDACTED]"
        elif email_re.search(person):
            person = "[EMAIL_REDACTED]"
            
        snippet_sanitized = phone_re.sub("[PHONE_REDACTED]", snippet)
        snippet_sanitized = email_re.sub("[EMAIL_REDACTED]", snippet_sanitized)
        
        clean_ev = {
            "person": person,
            "event_type": ev.get("event_type"),
            "inferred_date": ev.get("inferred_date"),
            "confidence": ev.get("confidence"),
            "source_snippet": snippet_sanitized,
            "reminder_timing": ev.get("reminder_timing", ["7 days before", "1 day before", "day of event"]),
            "suggested_action": ev.get("suggested_action"),
            "suggested_message": ev.get("suggested_message", ""),
            "status": ev.get("status", "captured")
        }
        sanitized_events.append(clean_ev)
        
    with open(events_path, "w", encoding="utf-8") as f:
        json.dump(sanitized_events, f, indent=2)
        
    return {
        "saved_count": len(sanitized_events),
        "path": "artifacts/events.json"
    }

@mcp.tool()
def list_captured_events() -> dict:
    """Return saved events for UI display."""
    events_path = os.path.join(ALLOWED_DIR, "artifacts", "events.json")
    if not os.path.exists(events_path):
        return {"events": []}
        
    with open(events_path, "r", encoding="utf-8") as f:
        events = json.load(f)
    return {"events": events}

@mcp.tool()
def generate_reminder_schedule(events: list) -> dict:
    """Generate default reminders for captured events.
    
    Args:
        events: List of event dictionaries.
    """
    reminders = []
    for ev in events:
        person = ev.get("person", "Unknown person")
        ev_type = ev.get("event_type", "event")
        date = ev.get("inferred_date", "")
        
        reminders.append({
            "person": person,
            "event_type": ev_type,
            "date": date,
            "reminders": [
                {"timing": "7 days before", "description": f"Reminder: 7 days until {person}'s {ev_type} ({date})"},
                {"timing": "1 day before", "description": f"Reminder: Tomorrow is {person}'s {ev_type}!"},
                {"timing": "day of event", "description": f"Alert: Today is {person}'s {ev_type}!"}
            ]
        })
    return {"reminders": reminders}

@mcp.tool()
def suggest_demo_actions(event_type: str, person: str, date: str, zip_code: str = None) -> dict:
    """Return mock message, e-card, flower, or call reminder suggestions.
    
    Args:
        event_type: The type of event.
        person: Name of the person.
        date: Inferred date.
        zip_code: Optional zip code for mock location-based flower search.
    """
    if event_type == "birthday":
        msg = f"Happy birthday, {person}! Wishing you a wonderful day and a year filled with joy! 🎂"
        suggested_action = "Draft message"
    elif event_type == "anniversary":
        msg = f"Happy anniversary, {person}! Wishing you both a beautiful celebration and many more happy years together! ❤️"
        suggested_action = "Find flowers"
    else:
        msg = f"Remembering {person} today with love. Keeping you and your family in my thoughts. 🙏"
        suggested_action = "Reminder to call"
        
    return {
        "suggested_message": msg,
        "actions": [
            {"label": "Draft message", "enabled": True, "type": "mock", "action_suggested": suggested_action},
            {"label": "Send e-card", "enabled": False, "type": "future"},
            {"label": "Find flowers", "enabled": False, "type": "future"},
            {"label": "Reminder to call", "enabled": True, "type": "mock"}
        ]
    }

@mcp.tool()
def write_audit_log(entry: dict) -> dict:
    """Write structured audit entries.
    
    Args:
        entry: The audit entry dictionary to log.
    """
    from app.privacy_utils import redact_pii

    artifacts_dir = os.path.join(ALLOWED_DIR, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    audit_path = os.path.join(artifacts_dir, "audit_log.jsonl")
    
    # Structure the entry according to the required capstone schema
    structured_entry = {
        "timestamp": entry.get("timestamp", entry.get("time", datetime.datetime.now().isoformat())),
        "agent": entry.get("agent", "System"),
        "action": entry.get("action", entry.get("event", "logged_action")),
        "decision": entry.get("decision", "none"),
        "confidence": entry.get("confidence", "n/a"),
        "input_summary": entry.get("input_summary", ""),
        "output_summary": entry.get("output_summary", ""),
        "security_flags": entry.get("security_flags", []),
        "saved_status": entry.get("saved_status", "success")
    }
    
    # Redact any values in the structured entry
    for k, v in structured_entry.items():
        if isinstance(v, str):
            structured_entry[k] = redact_pii(v)
        elif isinstance(v, list):
            structured_entry[k] = [redact_pii(item) if isinstance(item, str) else item for item in v]
            
    # Never log raw chat content
    structured_entry.pop("raw_chat", None)
    structured_entry.pop("chat_text", None)
    
    with open(audit_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(structured_entry) + "\n")
        
    return {
        "written": True,
        "path": "artifacts/audit_log.jsonl"
    }

if __name__ == "__main__":
    mcp.run()
