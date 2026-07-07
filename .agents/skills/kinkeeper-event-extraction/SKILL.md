---
name: kinkeeper-event-extraction
description: Use this skill when extracting birthdays, anniversaries, remembrance days, or family milestones from WhatsApp-style chat exports for KinKeeper.
---

# KinKeeper Event Extraction Skill

## Purpose

Extract likely family memories from WhatsApp-style chat text.

## Planning gate before extraction changes

Before changing extraction logic, define:

- what could go wrong
- what private data is protected
- edge cases
- tests and evals required
- privacy checks required

## Supported event types

- birthday
- anniversary
- remembrance day
- death anniversary

## Do not extract

- generic holiday greetings
- safe travels
- congratulations
- URLs alone
- media-only messages
- deleted messages
- system messages

## Extraction rules

1. Use the message timestamp as the likely event date.
2. Use the person name as it appears in the message.
3. If no person name appears, use `Unknown person`.
4. Assign confidence.
5. Merge duplicate wishes for the same person and event within a 2-day window.
6. Keep only short redacted source snippets.
7. Never store full raw chat.

## Confidence rules

High:

- clear event phrase
- clear person or couple name
- timestamp present

Medium:

- clear event phrase
- partial or nickname-style name

Low:

- event phrase
- no clear person name

## Examples

Input:

```text
[6/1/25, 8:12 AM] Sarah: Happy birthday Olivia!
```

Output:

```json
{
  "person": "Olivia",
  "event_type": "birthday",
  "date": "2025-06-01",
  "confidence": "high",
  "status": "captured"
}
```

Input:

```text
[6/1/25, 8:12 AM] Sarah: Happy birthday!
```

Output:

```json
{
  "person": "Unknown person",
  "event_type": "birthday",
  "date": "2025-06-01",
  "confidence": "low",
  "status": "needs_review"
}
```

## Validation checklist

Before returning extracted events, check:

- event type is supported
- date is inferred
- source snippet is short
- PII is redacted
- duplicates are merged
- ambiguous events are marked needs_review
