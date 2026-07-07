---
name: privacy-safe-memory
description: Use this skill when designing or reviewing KinKeeper features that process private chat exports, save memory records, or generate audit logs.
---

# Privacy-Safe Memory Skill

## Purpose

Ensure KinKeeper preserves family memories without exposing private chat data.

## Core rule

Save memories, not raw chats.

## Planning gate before memory changes

Before changing persistence, audit, or UI display logic, define:

- what could leak
- what is protected
- edge cases
- tests required
- security checks required

## Allowed to save

- person name as extracted
- event type
- date
- confidence
- status
- short redacted source snippet
- reminder settings
- audit summary

## Not allowed to save

- full raw WhatsApp export
- unredacted phone numbers
- unredacted emails
- full private message history
- API keys
- passwords
- payment data

## Required safeguards

- PII redaction
- prompt injection detection
- private path blocking
- no `.env` reads
- no auto-send
- no purchases
- audit logs

## Review checklist

For any feature, verify:

1. Does it require raw chat storage?
2. Can it work with structured events only?
3. Are snippets redacted?
4. Are private paths blocked?
5. Are external actions disabled?
6. Is the user able to edit/delete captured events?
7. Is there an audit log entry?

## Preferred language

Use privacy-forward language in UI:

```text
Raw chat is not stored. KinKeeper saves only structured event records.
```

Avoid:

```text
We save your chat history.
```
