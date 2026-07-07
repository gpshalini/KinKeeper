# ADK Architecture

## Goal

Build KinKeeper as an ADK multi-agent system.

The architecture must be simple enough to run locally, but clear enough to demonstrate meaningful agent design.

## Required ADK concepts

Use:

- ADK workflow graph
- Orchestrator agent
- Multiple specialized agents
- AgentTool for delegation
- Shared state through `ctx.state`
- Human editable UI flow, but not mandatory confirmation
- Security checkpoint node
- MCP tools used by at least two agents

## TDD and security planning requirements

Before writing the ADK workflow, create a short plan that answers:

- What could go wrong in agent routing?
- What data is protected in `ctx.state`?
- What edge cases could cause wrong extraction or wrong persistence?
- What tests prove each node works?
- What security checks must run before saving output?

The plan must specifically cover:

- duplicate route or duplicate edge risk
- raw chat accidentally stored in state or artifacts
- event extraction hallucinating names
- low-confidence events not being labeled correctly
- MCP tools reading unsafe paths
- UI showing unredacted snippets

## Agent list

### 1. KinKeeper Orchestrator Agent

Owns the end-to-end workflow.

Responsibilities:

- receive uploaded or pasted chat text
- call parser
- call extraction agent
- call privacy guard
- call reminder planner
- call concierge agent
- call audit report agent
- return final UI-ready response

### 2. Chat Parser Agent

Responsibilities:

- parse WhatsApp-style export lines
- identify timestamp, sender, message
- merge multiline messages
- skip system messages and media-only messages
- return structured message objects

### 3. Event Extraction Agent

Responsibilities:

- detect birthday, anniversary, remembrance, and death anniversary messages
- extract person name as written
- infer date from timestamp
- assign confidence
- detect repeated wishes and merge duplicates

### 4. Privacy Guard Agent

Responsibilities:

- redact phone numbers, emails, and likely addresses from snippets
- detect prompt injection text
- ensure raw chat is not stored
- flag unsafe content
- send security events to audit log

### 5. Reminder Planner Agent

Responsibilities:

- turn captured events into upcoming reminders
- use default reminders: 7 days before, 1 day before, day of
- sort events by upcoming date
- mark low-confidence events as needs_review

### 6. Message and Gift Concierge Agent

Responsibilities:

- generate a short suggested message
- suggest mock e-card, flowers, or reminder-to-call actions
- never send messages
- never make purchases
- return disabled or demo-only action metadata

### 7. Audit Report Agent

Responsibilities:

- summarize what was captured
- summarize what was skipped
- show privacy and security decisions
- show media skipped count
- show prompt injection detections
- show no raw chat stored

## Workflow state

Use `ctx.state` to store:

```text
raw_input_received
parsed_messages
skipped_messages
event_candidates
captured_events
needs_review_events
privacy_flags
security_events
audit_entries
ui_response
```

Do not store full raw chat in final persisted artifacts.

## Workflow shape

Recommended flow:

```text
User input
  -> security_checkpoint
  -> chat_parser
  -> event_extraction
  -> privacy_guard
  -> reminder_planner
  -> message_gift_concierge
  -> audit_report
  -> final_response
```

## Security checkpoint placement

Run security checks:

1. before parsing raw input
2. after event extraction
3. before persistence

## Duplicate event handling

Merge duplicates when:

```text
same normalized person
same event type
date within 2 days
```

Keep multiple source snippets as evidence, but cap snippets to avoid storing too much chat.

## Final response shape

Return:

```json
{
  "captured_events": [],
  "needs_review": [],
  "skipped_summary": {},
  "privacy_summary": {},
  "audit_summary": {},
  "suggested_actions": []
}
```

## Implementation notes

- Keep the first version small and working.
- Avoid overengineering relationship inference.
- Do not implement image reading.
- Do not implement live WhatsApp integration.
- Do not implement real marketplace API calls.
