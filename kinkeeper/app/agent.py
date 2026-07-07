import re
import datetime
from typing import Any

from google.adk.agents import LlmAgent, Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.workflow import Workflow, node
from google.adk.events.event import Event as AdkEvent
from google.adk.agents.context import Context
from google.genai import types

from app.models import ExtractionResult, ChatInput, WorkflowOutput, IdentityResult, ConciergeResult
from app.mcp_server import (
    read_sample_chat_export,
    save_captured_events,
    list_captured_events,
    generate_reminder_schedule,
    suggest_demo_actions,
    write_audit_log
)
from app.privacy_utils import redact_pii, detect_prompt_injection

# Helper function to extract text input from various types of ADK inputs
def extract_text(node_input: Any) -> str:
    if hasattr(node_input, "parts") and node_input.parts:
        return node_input.parts[0].text
    elif isinstance(node_input, dict) and "chat_text" in node_input:
        return node_input["chat_text"]
    elif hasattr(node_input, "chat_text"):
        return getattr(node_input, "chat_text")
    elif isinstance(node_input, str):
        return node_input
    return str(node_input)

# 1. Security Checkpoint: Detect and sanitize prompt injections
def security_checkpoint(ctx: Context, node_input: Any) -> str:
    chat_text = extract_text(node_input)
    
    # Check if the input is actually a file path
    if len(chat_text.strip()) < 250 and (chat_text.strip().endswith(".txt") or "data/" in chat_text):
        # Call MCP tool read_sample_chat_export to read the file
        read_res = read_sample_chat_export(chat_text.strip())
        if "error" in read_res:
            chat_text = f"ERROR: {read_res['error']}"
        else:
            chat_text = read_res["content"]
            
    ctx.state["raw_input_received"] = True
    ctx.state["security_events"] = ctx.state.get("security_events", [])
    ctx.state["privacy_flags"] = ctx.state.get("privacy_flags", {})
    
    # Use detect_prompt_injection from privacy_utils
    matches = detect_prompt_injection(chat_text)
    is_unsafe = len(matches) > 0
    sanitized_text = chat_text
    
    if is_unsafe:
        for match in matches:
            security_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "event": "Prompt Injection Detected",
                "pattern": match,
                "agent": "Security Checkpoint",
                "decision": "sanitize_input",
                "security_flags": ["prompt_injection"]
            }
            ctx.state["security_events"].append(security_entry)
            
            # Call MCP tool write_audit_log immediately for security violation
            write_audit_log(security_entry)
            
        # Strip lines containing prompt injections to prevent execution
        lines = chat_text.splitlines()
        cleaned_lines = []
        for line in lines:
            line_matches = detect_prompt_injection(line)
            if not line_matches:
                cleaned_lines.append(line)
        sanitized_text = "\n".join(cleaned_lines)
        ctx.state["privacy_flags"]["unsafe_content_detected"] = True
        
    return sanitized_text

# 2. Chat Parser: Clean the export, handle multiline messages, and filter ignores
def chat_parser(ctx: Context, node_input: str) -> list[dict[str, Any]]:
    # If the checkpoint returned an error, don't parse
    if node_input.startswith("ERROR:"):
        ctx.state["parsed_messages"] = []
        ctx.state["skipped_messages"] = [{"line": node_input, "reason": "checkpoint_error"}]
        ctx.state["media_skipped_count"] = 0
        return []
        
    lines = node_input.splitlines()
    parsed_messages = []
    skipped_messages = []
    media_skipped_count = 0
    
    # Bracketed: [7/3/26, 9:00:00 AM] Sender: Message
    # Bracketed: [7/3/26, 9:00 AM] or [7/3/26, 9:00:00 AM] Sender: Message
    bracket_re = re.compile(
        r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*([^:]+):\s*(.*)$", 
        re.IGNORECASE
    )
    # Dash style: 7/3/26, 9:00 AM - Sender: Message or 7/3/26, 9:00:00 AM - Sender: Message
    dash_re = re.compile(
        r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\s*-\s*([^:]+):\s*(.*)$", 
        re.IGNORECASE
    )
    
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
                parsed_messages.append(current_message)
            current_message = {
                "date": date_str, 
                "time": time_str, 
                "sender": sender, 
                "content": content
            }
        elif m_dash:
            date_str, time_str, sender, content = m_dash.groups()
            if current_message:
                parsed_messages.append(current_message)
            current_message = {
                "date": date_str, 
                "time": time_str, 
                "sender": sender, 
                "content": content
            }
        else:
            if current_message:
                current_message["content"] += "\n" + line
            else:
                skipped_messages.append({
                    "line": line, 
                    "reason": "unparsed_system_or_metadata"
                })
                
    if current_message:
        parsed_messages.append(current_message)
        
    filtered_messages = []
    system_keywords = [
        "created this group", 
        "added", 
        "changed the subject", 
        "Messages and calls are end-to-end encrypted"
    ]
    media_keywords = [
        "image omitted", 
        "GIF omitted", 
        "video omitted", 
        "audio omitted", 
        "sticker omitted"
    ]
    deleted_keywords = [
        "This message was deleted", 
        "This message was deleted."
    ]
    
    for msg in parsed_messages:
        content = msg["content"].strip()
        sender = msg["sender"].strip()
        
        is_skipped = False
        skip_reason = ""
        
        if any(kw in content for kw in media_keywords):
            is_skipped = True
            skip_reason = "media_omitted"
            media_skipped_count += 1
        elif any(kw in content for kw in deleted_keywords):
            is_skipped = True
            skip_reason = "deleted_message"
        elif any(kw in content for kw in system_keywords) or any(kw in sender for kw in system_keywords):
            is_skipped = True
            skip_reason = "system_message"
            
        if is_skipped:
            skipped_messages.append({
                "sender": sender, 
                "content": content, 
                "reason": skip_reason
            })
        else:
            filtered_messages.append(msg)
            
    ctx.state["parsed_messages"] = filtered_messages
    ctx.state["skipped_messages"] = skipped_messages
    ctx.state["media_skipped_count"] = media_skipped_count
    
    return filtered_messages

# 3. Event Extraction Agent: LlmAgent that identifies family events
event_extractor = LlmAgent(
    name="event_extractor",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    Analyze the provided list of parsed chat messages and extract family events (birthdays, anniversaries, remembrance days, and death anniversaries).

    For each event:
    1. Extract the name of the person being wished. If the name is not clear, return "Unknown person".
    2. Identify the event type: "birthday", "anniversary", "remembrance day", or "death anniversary".
    3. Infer the date in YYYY-MM-DD format (use the message date if not explicitly specified).
    4. Determine the confidence:
       - "high": clear event phrase, clear name, clear date
       - "medium": event phrase with partial or nickname name
       - "low": event phrase but no name (e.g. "Happy birthday!") or ambiguous text.
    5. Keep the exact chat message text as the source_snippet.
    
    Strictly ignore standard holiday greetings like "Happy New Year", "Merry Christmas", or "Congratulations" unless they explicitly represent a personal birthday/anniversary/remembrance.
    """,
    output_schema=ExtractionResult,
)

# 3b. Identity & Relationship Agent: Deduplicate, resolve nicknames and standard names
identity_resolver = LlmAgent(
    name="identity_resolver",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    Analyze the extracted family events list and:
    1. Deduplicate/merge events for the same person and event type occurring within a 2-day window (e.g., late or early wishes, time zone differences).
       - Merge their source snippets separated by a divider: "\n---\n".
       - Keep the earlier inferred date.
       - Standardize confidence: if any duplicate has high confidence, the merged confidence is "high".
    2. Standardize nicknames (e.g., if one is 'Liv' and another is 'Olivia', resolve them both to 'Olivia').
    3. If a group is wished together (e.g., 'Lisa and David' anniversary), keep them as 'Lisa and David' if they share the anniversary.
    4. Ensure the output is formatted strictly as an IdentityResult list.
    """,
    output_schema=IdentityResult,
)

# 3c. Creative Concierge Agent: Suggest personalized messages and concierge actions
creative_concierge = LlmAgent(
    name="creative_concierge",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""
    For each resolved family event:
    1. Draft a warm, context-aware personalized greeting wish message:
       - For birthdays: generate a joyful wish (e.g., "Happy birthday, [Name]! Wishing you a wonderful day and a year filled with joy! 🎂").
       - For anniversaries: generate a congratulatory wish (e.g., "Happy anniversary, [Names]! Wishing you both a beautiful celebration and many more happy years together! ❤️").
       - For remembrances/death anniversaries: generate a warm, respectful note (e.g., "Remembering [Name] today with love. Keeping you and your family in my thoughts. 🙏").
       - If the person is 'Unknown person', keep the greeting neutral and warm.
    2. Recommend one of the following exact concierge actions as suggested_action:
       - "Draft message" (default)
       - "Send e-card"
       - "Find flowers"
       - "Reminder to call"
       Use your best judgment based on the event type (e.g., anniversary -> "Send e-card" or "Find flowers", remembrance -> "Reminder to call", birthday -> "Draft message").
    3. Ensure the output conforms strictly to ConciergeResult.
    """,
    output_schema=ConciergeResult,
)

# 4. Privacy Guard: Redact phone numbers, emails, addresses, secrets, and URLs
def privacy_guard(ctx: Context, node_input: ConciergeResult) -> list[dict[str, Any]]:
    sanitized_events = []
    
    for ev in node_input.events:
        person = redact_pii(ev.person)
        snippet = redact_pii(ev.source_snippet)
        suggested_message = redact_pii(ev.suggested_message)
        
        sanitized_events.append({
            "person": person,
            "event_type": ev.event_type,
            "inferred_date": ev.inferred_date,
            "confidence": ev.confidence,
            "source_snippet": snippet,
            "suggested_action": ev.suggested_action,
            "suggested_message": suggested_message,
            "status": "captured"
        })
        
    ctx.state["event_candidates"] = sanitized_events
    
    # Log privacy protection audit event if redaction occurred
    has_redactions = False
    for e in sanitized_events:
        if "[PHONE_REDACTED]" in e["source_snippet"] or "[PHONE_REDACTED]" in e["person"] or \
           "[EMAIL_REDACTED]" in e["source_snippet"] or "[EMAIL_REDACTED]" in e["person"] or \
           "[ADDRESS_REDACTED]" in e["source_snippet"] or "[SECRET_REDACTED]" in e["source_snippet"]:
            has_redactions = True
            break
            
    if has_redactions:
        write_audit_log({
            "timestamp": datetime.datetime.now().isoformat(),
            "event": "Privacy Redaction Triggered",
            "agent": "Privacy Guard",
            "decision": "redact_pii",
            "input_summary": "Extracted events containing PII",
            "output_summary": "Sanitized events successfully"
        })
        
    return sanitized_events

# 5. Reminder Planner: Create reminders, flag low confidence, and sort
def reminder_planner(ctx: Context, node_input: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Call MCP tool generate_reminder_schedule to build reminders
    reminders_res = generate_reminder_schedule(node_input)
    reminders_map = {r["person"] + "_" + r["event_type"]: r["reminders"] for r in reminders_res.get("reminders", [])}
    
    final_events = []
    for ev in node_input:
        person = ev["person"]
        ev_type = ev["event_type"]
        key = person + "_" + ev_type
        
        # Get timings list
        raw_reminders = reminders_map.get(key, [])
        timings = [r["timing"] for r in raw_reminders]
        if not timings:
            timings = ["7 days before", "1 day before", "day of event"]
            
        status = "captured"
        if ev["confidence"] == "low" or ev["person"] == "Unknown person":
            status = "needs_review"
            
        suggested_action = ev.get("suggested_action", "Draft message")
        suggested_msg = ev.get("suggested_message", "")
        
        final_events.append({
            **ev,
            "reminder_timing": timings,
            "suggested_action": suggested_action,
            "suggested_message": suggested_msg,
            "status": status
        })
        
    def get_sort_key(e):
        date_str = e["inferred_date"]
        try:
            parts = date_str.split("-")
            if len(parts) == 3:
                return (int(parts[1]), int(parts[2]))
        except Exception:
            pass
        return (12, 31)
        
    final_events.sort(key=get_sort_key)
    
    ctx.state["captured_events"] = [e for e in final_events if e["status"] == "captured"]
    ctx.state["needs_review_events"] = [e for e in final_events if e["status"] == "needs_review"]
    
    # Call MCP tool save_captured_events to persist to disk
    save_captured_events(final_events)
    
    return final_events

# 6. Concierge Node: Place-holder node (concierge tasks are already handled by creative_concierge)
def concierge_node(ctx: Context, node_input: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return node_input

# 7. Audit Report: Summarize execution details and privacy decisions
def audit_report(ctx: Context, node_input: list[dict[str, Any]]) -> dict[str, Any]:
    parsed_count = len(ctx.state.get("parsed_messages", []))
    skipped_count = len(ctx.state.get("skipped_messages", []))
    media_skipped = ctx.state.get("media_skipped_count", 0)
    security_alerts = len(ctx.state.get("security_events", []))
    
    captured_count = len(ctx.state.get("captured_events", []))
    needs_review_count = len(ctx.state.get("needs_review_events", []))
    
    audit_summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "messages_parsed": parsed_count,
        "messages_skipped": skipped_count,
        "media_files_ignored": media_skipped,
        "security_violations_logged": security_alerts,
        "events_captured": captured_count,
        "events_flagged_for_review": needs_review_count,
        "no_raw_chat_stored_confirmed": True
    }
    
    # Call MCP tool write_audit_log to save the audit report to disk
    write_audit_log(audit_summary)
    
    ctx.state["audit_entries"] = ctx.state.get("audit_entries", [])
    ctx.state["audit_entries"].append(audit_summary)
    
    return audit_summary

# 8. Final Response: Format output to match the required UI schema
def final_response(ctx: Context, node_input: dict[str, Any]) -> dict[str, Any]:
    captured = ctx.state.get("captured_events", [])
    needs_review = ctx.state.get("needs_review_events", [])
    skipped = ctx.state.get("skipped_messages", [])
    
    skipped_summary = {
        "total_skipped": len(skipped),
        "media_omitted_count": ctx.state.get("media_skipped_count", 0),
        "deleted_messages_skipped": sum(1 for m in skipped if m.get("reason") == "deleted_message"),
        "system_messages_skipped": sum(1 for m in skipped if m.get("reason") == "system_message"),
    }
    
    privacy_summary = {
        "phone_numbers_redacted_count": sum(
            1 for e in captured + needs_review 
            if "[PHONE_REDACTED]" in e["source_snippet"] or "[PHONE_REDACTED]" in e["person"]
        ),
        "emails_redacted_count": sum(
            1 for e in captured + needs_review 
            if "[EMAIL_REDACTED]" in e["source_snippet"] or "[EMAIL_REDACTED]" in e["person"]
        ),
        "unsafe_content_blocked": "unsafe_content_detected" in ctx.state.get("privacy_flags", {})
    }
    
    suggested_actions = []
    for ev in captured + needs_review:
        suggested_actions.append({
            "person": ev["person"],
            "event_type": ev["event_type"],
            "action": ev["suggested_action"],
            "message_draft": ev.get("suggested_message", "")
        })
        
    response = {
        "captured_events": captured,
        "needs_review": needs_review,
        "skipped_summary": skipped_summary,
        "privacy_summary": privacy_summary,
        "audit_summary": ctx.state["audit_entries"][-1] if ctx.state.get("audit_entries") else {},
        "suggested_actions": suggested_actions
    }
    
    ctx.state["ui_response"] = response
    return response

# Define the workflow graph
root_agent = Workflow(
    name="root_agent",
    edges=[
        ('START', security_checkpoint),
        (security_checkpoint, chat_parser),
        (chat_parser, event_extractor),
        (event_extractor, identity_resolver),
        (identity_resolver, creative_concierge),
        (creative_concierge, privacy_guard),
        (privacy_guard, reminder_planner),
        (reminder_planner, concierge_node),
        (concierge_node, audit_report),
        (audit_report, final_response)
    ],
    output_schema=WorkflowOutput
)

app = App(
    root_agent=root_agent,
    name="app",
)
