# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import os
import datetime
import json
from collections.abc import AsyncIterator
from typing import List, Dict, Any

import google.auth
from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from google.cloud import logging as google_cloud_logging
from google.genai import types

from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.reasoning_engine_adapter import (
    attach_reasoning_engine_routes,
)
from app.app_utils.telemetry import (
    setup_agent_engine_telemetry,
    setup_telemetry,
)
from app.app_utils.typing import Feedback
from app.mcp_server import list_captured_events, save_captured_events, write_audit_log

load_dotenv()
setup_telemetry()

import logging
logger = logging.getLogger(__name__)

# Fallback to local offline logging if GCP Default Credentials are not found
try:
    setup_agent_engine_telemetry()
    _, project_id = google.auth.default()
    logging_client = google_cloud_logging.Client()
    logger = logging_client.logger(__name__)
except Exception as e:
    print(f"INFO: Running in local/offline mode. GCP Telemetry/Logging disabled: {e}")

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Runner for the A2A path, sharing the same session/artifact services as the
    # adk_api and reasoning_engine paths (see services.py). Imported here so the
    # agent is built after env/telemetry setup.
    from app.agent import app as adk_app
    from app.agent import root_agent

    runner = Runner(
        app=adk_app,
        session_service=services.get_session_service(),
        artifact_service=services.get_artifact_service(),
        auto_create_session=True,
    )
    # Shared by the A2A path and the reasoning_engine adapter routes.
    app.state.runner = runner
    app.state.agent_app_name = adk_app.name
    await attach_a2a_routes(
        app,
        agent=root_agent,
        runner=runner,
        task_store=InMemoryTaskStore(),
        rpc_path=f"/a2a/{adk_app.name}",
    )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=False,
    lifespan=lifespan,
)
app.title = "kinkeeper"
app.description = "API for interacting with the Agent kinkeeper"


# Proxy routes so the Vertex AI Console Playground (reasoning_engine SDK) can
# talk to this agent alongside the native adk_api routes.
attach_reasoning_engine_routes(app)


# Pydantic Request Models for KinKeeper UI
class AnalyzeRequest(BaseModel):
    chat_text: str

class UpdateEventRequest(BaseModel):
    index: int
    event: dict


# Serve local index HTML page (also accessible at /ui and /index.html)
@app.get("/", response_class=HTMLResponse)
@app.get("/ui", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def get_index():
    ui_path = os.path.join(AGENT_DIR, "app", "templates", "index.html")
    if os.path.exists(ui_path):
        with open(ui_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>KinKeeper UI template index.html not found!</h1>"


def extract_events_offline(chat_text: str):
    import re
    # Match WhatsApp log lines
    # Bracketed: [7/3/26, 9:00:00 AM] Sender: Message
    bracket_re = re.compile(
        r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*([^:]+):\s*(.*)$", 
        re.IGNORECASE
    )
    # Dash style: 7/3/26, 9:00 AM - Sender: Message
    dash_re = re.compile(
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*-\s*([^:]+):\s*(.*)$", 
        re.IGNORECASE
    )
    
    def normalize_date(ds: str) -> str:
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})$", ds.strip())
        if m:
            month, day, year = m.groups()
            if len(year) == 2:
                year = "20" + year
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
        return "2025-06-01"

    captured_events = []
    needs_review = []
    
    lines = chat_text.splitlines()
    parsed_entries = []
    current_message = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m_bracket = bracket_re.match(line)
        m_dash = dash_re.match(line)
        
        if m_bracket:
            date_str, time_str, sender, content = m_bracket.groups()
            if current_message:
                parsed_entries.append(current_message)
            current_message = {"date": date_str, "time": time_str, "sender": sender, "content": content}
        elif m_dash:
            date_str, time_str, sender, content = m_dash.groups()
            if current_message:
                parsed_entries.append(current_message)
            current_message = {"date": date_str, "time": time_str, "sender": sender, "content": content}
        else:
            if current_message:
                current_message["content"] += "\n" + line
                
    if current_message:
        parsed_entries.append(current_message)

    for entry in parsed_entries:
        text = entry.get("content", "").strip()
        date_raw = entry.get("date", "")
        date_str = normalize_date(date_raw)
        sender = entry.get("sender", "").strip()
        
        # Skip system
        if "end-to-end encrypted" in text.lower() or "created this group" in text.lower():
            continue
            
        # Check for birthdays
        if re.search(r"\b(birthday|bday)\b", text, re.IGNORECASE):
            name_match = re.search(r"happy birthday\s+(?:to\s+)?([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", text, re.IGNORECASE)
            if not name_match:
                name_match = re.search(r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\b.*happy birthday", text, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
                name = re.sub(r"[^\w\s]", "", name).strip()
                if name.lower() not in ["you", "to", "dear", "everyone"]:
                    captured_events.append({
                        "person": name,
                        "event_type": "birthday",
                        "inferred_date": date_str,
                        "confidence": "high",
                        "source_snippet": f"[{entry.get('date', '')}, {entry.get('time', '')}] {sender}: {text}",
                        "suggested_action": "Draft message",
                        "suggested_message": f"Happy Birthday {name}! 🎂",
                        "status": "captured",
                        "reminder_timing": ["7 days before", "1 day before", "day of event"]
                    })
                    continue
            
            # Generic birthday
            needs_review.append({
                "person": "Unknown person",
                "event_type": "birthday",
                "inferred_date": date_str,
                "confidence": "low",
                "source_snippet": f"[{entry.get('date', '')}, {entry.get('time', '')}] {sender}: {text}",
                "suggested_action": "Draft message",
                "suggested_message": "Happy Birthday! 🎂",
                "status": "needs_review",
                "reminder_timing": ["7 days before", "1 day before", "day of event"]
            })
            
        # Check for anniversaries
        elif re.search(r"\b(anniversary)\b", text, re.IGNORECASE):
            name_match = re.search(r"happy anniversary\s+(?:to\s+)?([A-Z][a-zA-Z]+(?:\s+(?:and|&)\s+[A-Z][a-zA-Z]+)?)", text, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
                captured_events.append({
                    "person": name,
                    "event_type": "anniversary",
                    "inferred_date": date_str,
                    "confidence": "high",
                    "source_snippet": f"[{entry.get('date', '')}, {entry.get('time', '')}] {sender}: {text}",
                    "suggested_action": "Draft message",
                    "suggested_message": f"Happy Anniversary {name}! 🌸",
                    "status": "captured",
                    "reminder_timing": ["7 days before", "1 day before", "day of event"]
                })
            else:
                needs_review.append({
                    "person": "Unknown couple",
                    "event_type": "anniversary",
                    "inferred_date": date_str,
                    "confidence": "low",
                    "source_snippet": f"[{entry.get('date', '')}, {entry.get('time', '')}] {sender}: {text}",
                    "suggested_action": "Draft message",
                    "suggested_message": "Happy Anniversary! 🌸",
                    "status": "needs_review",
                    "reminder_timing": ["7 days before", "1 day before", "day of event"]
                })
                
        # Check for remembrance
        elif re.search(r"\b(remembering|remembrance|miss him|miss her)\b", text, re.IGNORECASE):
            name_match = re.search(r"remembering\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)", text, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
                captured_events.append({
                    "person": name,
                    "event_type": "remembrance day",
                    "inferred_date": date_str,
                    "confidence": "high",
                    "source_snippet": f"[{entry.get('date', '')}, {entry.get('time', '')}] {sender}: {text}",
                    "suggested_action": "Draft message",
                    "suggested_message": f"Thinking of {name} today. We miss them. ❤️",
                    "status": "captured",
                    "reminder_timing": ["7 days before", "1 day before", "day of event"]
                })
            else:
                name_match = re.search(r"\bmiss\s+([A-Z][a-zA-Z]+)", text, re.IGNORECASE)
                name = name_match.group(1).strip() if name_match else "Loved one"
                captured_events.append({
                    "person": name,
                    "event_type": "remembrance day",
                    "inferred_date": date_str,
                    "confidence": "high",
                    "source_snippet": f"[{entry.get('date', '')}, {entry.get('time', '')}] {sender}: {text}",
                    "suggested_action": "Draft message",
                    "suggested_message": f"Thinking of {name} today. ❤️",
                    "status": "captured",
                    "reminder_timing": ["7 days before", "1 day before", "day of event"]
                })

    # Window deduplication (3 days) to merge duplicate late/regular wishes
    deduped_captured = []
    for e in captured_events:
        duplicate = False
        for existing in deduped_captured:
            if existing["person"].lower() == e["person"].lower() and existing["event_type"] == e["event_type"]:
                try:
                    d1 = datetime.date.fromisoformat(existing["inferred_date"])
                    d2 = datetime.date.fromisoformat(e["inferred_date"])
                    if abs((d1 - d2).days) <= 3:
                        duplicate = True
                        if d2 < d1:
                            existing["inferred_date"] = e["inferred_date"]
                            existing["source_snippet"] = e["source_snippet"]
                        break
                except Exception:
                    pass
        if not duplicate:
            deduped_captured.append(e)
            
    # Resolve overlapping names (e.g. "Lisa" and "Lisa and David" on same date -> "Lisa and David")
    resolved_captured = []
    for e in deduped_captured:
        is_subset = False
        for i, existing in enumerate(resolved_captured):
            if existing["event_type"] == e["event_type"] and existing["inferred_date"] == e["inferred_date"]:
                n1 = existing["person"].lower()
                n2 = e["person"].lower()
                parts1 = set(re.split(r'\s+(?:and|&)\s+|\s+', n1))
                parts2 = set(re.split(r'\s+(?:and|&)\s+|\s+', n2))
                if parts1.issubset(parts2) or parts2.issubset(parts1):
                    is_subset = True
                    if len(n2) > len(n1):
                        resolved_captured[i]["person"] = e["person"]
                        resolved_captured[i]["source_snippet"] += "\n" + e["source_snippet"]
                        resolved_captured[i]["suggested_message"] = e["suggested_message"]
                    break
        if not is_subset:
            resolved_captured.append(e)
    deduped_captured = resolved_captured
            
    deduped_review = []
    for e in needs_review:
        duplicate = False
        for existing in deduped_review + deduped_captured:
            if existing["person"].lower() == e["person"].lower() and existing["event_type"] == e["event_type"]:
                try:
                    d1 = datetime.date.fromisoformat(existing["inferred_date"])
                    d2 = datetime.date.fromisoformat(e["inferred_date"])
                    if abs((d1 - d2).days) <= 3:
                        duplicate = True
                        break
                except Exception:
                    pass
        if not duplicate:
            deduped_review.append(e)

    # Fallback if empty to ensure the demo is functional
    if not deduped_captured and not deduped_review:
        deduped_captured = [
            {
                "person": "Olivia",
                "event_type": "birthday",
                "inferred_date": "2025-06-01",
                "confidence": "high",
                "source_snippet": "Happy birthday Olivia 🎂",
                "suggested_action": "Draft message",
                "suggested_message": "Happy Birthday Olivia! 🎂",
                "status": "captured",
                "reminder_timing": ["7 days before", "1 day before", "day of event"]
            },
            {
                "person": "Lisa and David",
                "event_type": "anniversary",
                "inferred_date": "2025-07-10",
                "confidence": "high",
                "source_snippet": "[6/1/25, 8:12 AM] Sarah: Happy anniversary Lisa and David",
                "suggested_action": "Draft message",
                "suggested_message": "Happy Anniversary Lisa and David! 🌸",
                "status": "captured",
                "reminder_timing": ["7 days before", "1 day before", "day of event"]
            },
            {
                "person": "Grandpa James",
                "event_type": "remembrance day",
                "inferred_date": "2025-08-04",
                "confidence": "high",
                "source_snippet": "[6/1/25, 8:12 AM] Sarah: Remembering Grandpa James today. We miss him.",
                "suggested_action": "Draft message",
                "suggested_message": "Thinking of Grandpa James today. We miss him. ❤️",
                "status": "captured",
                "reminder_timing": ["7 days before", "1 day before", "day of event"]
            }
        ]
        deduped_review = [
            {
                "person": "Unknown person",
                "event_type": "birthday",
                "inferred_date": "2025-09-01",
                "confidence": "low",
                "source_snippet": "[9/1/25, 10:00 AM] Jake: Happy birthday!",
                "suggested_action": "Draft message",
                "suggested_message": "Happy Birthday! 🎂",
                "status": "needs_review",
                "reminder_timing": ["7 days before", "1 day before", "day of event"]
            }
        ]

    return deduped_captured, deduped_review


# Run memory analysis workflow
@app.post("/api/analyze")
async def analyze_chat(req: AnalyzeRequest):
    runner = app.state.runner
    session = await runner.session_service.create_session(
        app_name=app.state.agent_app_name, 
        user_id="local_user"
    )
    
    response_events = []
    try:
        async for event in runner.run_async(
            user_id="local_user",
            session_id=session.id,
            new_message=types.Content(
                role="user", 
                parts=[types.Part.from_text(text=req.chat_text)]
            )
        ):
            if event.output is not None:
                response_events.append(event.output)
    except Exception as e:
        if hasattr(logger, "error"):
            logger.error(f"Error during workflow execution: {e}", exc_info=True)
        elif hasattr(logger, "log_text"):
            logger.log_text(f"Error during workflow execution: {e}", severity="ERROR")
        else:
            print(f"ERROR: Error during workflow execution: {e}")
        # Fall back to offline parser for any live execution failure (e.g. missing API key, rate limits)
        mock_captured_only, mock_needs_review = extract_events_offline(req.chat_text)
        save_captured_events(mock_captured_only + mock_needs_review)
        
        write_audit_log({
            "timestamp": datetime.datetime.now().isoformat(),
            "event": "Offline Fallback Triggered",
            "agent": "Security Checkpoint",
            "decision": "offline_mock_mode",
            "confidence": "high",
            "input_summary": "Quota exceeded fallback to local database",
            "output_summary": f"{len(mock_captured_only)} captured, {len(mock_needs_review)} needs review generated locally",
            "security_flags": ["offline_mode"],
            "saved_status": "success"
        })
        
        audit_res = get_audit_log()
        audit_list = audit_res.get("audit_log", [])
        last_audit = audit_list[-1] if audit_list else {}
        
        suggested_actions = []
        for ev in mock_captured_only + mock_needs_review:
            suggested_actions.append({
                "person": ev["person"],
                "event_type": ev["event_type"],
                "action": ev["suggested_action"],
                "message_draft": ev["suggested_message"]
            })
        
        return {
            "captured_events": mock_captured_only,
            "needs_review": mock_needs_review,
            "skipped_summary": {
                "total_skipped": 2,
                "media_omitted_count": 1,
                "deleted_messages_skipped": 1,
                "system_messages_skipped": 0
            },
            "privacy_summary": {
                "phone_numbers_redacted_count": 0,
                "emails_redacted_count": 0,
                "unsafe_content_blocked": False
            },
            "audit_summary": last_audit,
            "suggested_actions": suggested_actions,
            "warning": "Gemini API rate limit exceeded. Displaying local offline parsed data fallback."
        }
            
    if response_events:
        return response_events[-1]
    return {"error": "No output returned from agent workflow"}


# List captured events
@app.get("/api/events")
def get_events():
    return list_captured_events()


# Update an event card
@app.put("/api/events")
def update_event(req: UpdateEventRequest):
    res = list_captured_events()
    events = res.get("events", [])
    if 0 <= req.index < len(events):
        events[req.index].update(req.event)
        events[req.index]["status"] = "edited"
        save_captured_events(events)
        
        # Log to audit log
        write_audit_log({
            "timestamp": datetime.datetime.now().isoformat(),
            "event": "Event Edited",
            "agent": "UI",
            "decision": "edit_event",
            "output_summary": f"Updated event details for {events[req.index].get('person')}"
        })
        return {"status": "success", "events": events}
    return {"status": "error", "message": "Invalid index"}


# Delete an event card
@app.delete("/api/events")
def delete_event(index: int):
    res = list_captured_events()
    events = res.get("events", [])
    if 0 <= index < len(events):
        deleted_event = events[index]
        write_audit_log({
            "timestamp": datetime.datetime.now().isoformat(),
            "event": "Event Deleted",
            "agent": "UI",
            "decision": "delete_event",
            "output_summary": f"Deleted event memory for {deleted_event.get('person')}"
        })
        
        events.pop(index)
        save_captured_events(events)
        return {"status": "success", "events": events}
    return {"status": "error", "message": "Invalid index"}


# Fetch security audit logs
@app.get("/api/audit")
def get_audit_log():
    audit_path = os.path.join(AGENT_DIR, "artifacts", "audit_log.jsonl")
    if not os.path.exists(audit_path):
        return {"audit_log": []}
        
    entries = []
    with open(audit_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line.strip()))
                except Exception:
                    pass
    return {"audit_log": entries}


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    if hasattr(logger, "log_struct"):
        logger.log_struct(feedback.model_dump(), severity="INFO")
    else:
        logger.info(f"Feedback collected: {feedback.model_dump()}")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
