# MCP Tools

## Goal

Build a local MCP server for KinKeeper so the project clearly demonstrates MCP in code.

The MCP server should expose tools that agents can call for local data access, event persistence, reminder generation, and mock concierge suggestions.

## File location

Generated project should include:

```text
<project_source_dir>/mcp_server.py
```

The exact source directory is whatever Agents CLI creates and that contains `agent.py`.

## TDD and security planning requirements

Before writing MCP tools, create a short plan that answers:

- What could go wrong if a tool reads the wrong file?
- What files and secrets are protected?
- What edge cases must the tools reject?
- What tests prove the tools are safe?
- What audit entries should each tool create?

The plan must cover:

- `.env` read attempts
- `data/private` read attempts
- very large file attempts
- zip upload attempts
- raw chat persistence attempts
- unredacted snippet persistence
- mock action accidentally becoming real external action

## Transport

Use stdio transport for the local MCP server.

## Required tools

### 1. `read_sample_chat_export`

Purpose:

Read the synthetic demo file.

Input:

```json
{
  "file_path": "data/sample_whatsapp_export.txt"
}
```

Output:

```json
{
  "content": "...",
  "source": "synthetic_sample",
  "safe_for_demo": true
}
```

Rules:

- Refuse paths under `data/private`
- Refuse zip files
- Refuse files larger than a reasonable local demo limit
- Never read `.env`

### 2. `save_captured_events`

Purpose:

Save structured captured events to local artifacts.

Input:

```json
{
  "events": []
}
```

Output:

```json
{
  "saved_count": 0,
  "path": "artifacts/events.json"
}
```

Rules:

- Save only structured event data
- Do not save raw chat
- Redact snippets before saving

### 3. `list_captured_events`

Purpose:

Return saved events for UI display.

Input:

```json
{}
```

Output:

```json
{
  "events": []
}
```

### 4. `generate_reminder_schedule`

Purpose:

Generate default reminders for captured events.

Input:

```json
{
  "events": []
}
```

Output:

```json
{
  "reminders": []
}
```

Default reminders:

- 7 days before
- 1 day before
- day of event

### 5. `suggest_demo_actions`

Purpose:

Return mock message, e-card, flower, or call reminder suggestions.

Input:

```json
{
  "event_type": "birthday",
  "person": "Olivia",
  "date": "2025-06-01",
  "zip_code": "optional"
}
```

Output:

```json
{
  "suggested_message": "...",
  "actions": [
    {"label": "Draft message", "enabled": true, "type": "mock"},
    {"label": "Send e-card", "enabled": false, "type": "future"},
    {"label": "Find flowers", "enabled": false, "type": "future"}
  ]
}
```

Rules:

- No real external API calls
- No purchases
- No sending messages

### 6. `write_audit_log`

Purpose:

Write structured audit entries.

Input:

```json
{
  "entry": {}
}
```

Output:

```json
{
  "written": true,
  "path": "artifacts/audit_log.jsonl"
}
```

Rules:

- Do not log full raw chat
- Log summaries and redacted snippets only

## Agents that should use MCP tools

| Agent | MCP tool use |
|---|---|
| Chat Parser Agent | `read_sample_chat_export` |
| Reminder Planner Agent | `save_captured_events`, `list_captured_events`, `generate_reminder_schedule` |
| Message and Gift Concierge Agent | `suggest_demo_actions` |
| Audit Report Agent | `write_audit_log` |
| Privacy Guard Agent | may call `write_audit_log` |

## Security rules for MCP tools

MCP tools must:

- validate inputs
- reject unsafe paths
- never read `.env`
- never read private exports by default
- never save raw chat text
- return structured JSON
- provide clear error messages

## README requirement

Document every MCP tool in the final README and submission writeup.
