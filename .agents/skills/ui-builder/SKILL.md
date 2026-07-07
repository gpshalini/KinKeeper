---
name: ui-builder
description: Use this skill when building or improving the KinKeeper local UI for upload, analysis, captured memories, edit/delete actions, and privacy audit.
---

# KinKeeper UI Builder Skill

## Purpose

Build a simple, warm, functional UI for KinKeeper.

## Planning gate before UI changes

Before building or changing UI, define:

- what could go wrong for the user
- what private data could appear on screen
- edge cases
- UI tests required
- privacy checks required

## UI principles

- Functionality first
- Pastel, elegant, warm, and calm
- Privacy-forward
- Easy to scan
- No dense enterprise dashboard
- No dark hacker style
- No neon-heavy styling
- No complex animations in first pass

## Required UI sections

1. Header
2. Upload or paste input
3. Analyze Memories button
4. Captured memories list
5. Needs review cards
6. Edit/delete controls
7. Suggested actions
8. Privacy audit summary

## Event card requirements

Each card should show:

- person
- event type
- date
- confidence
- status
- source snippet
- reminders
- suggested action
- Edit
- Delete

## Privacy audit requirements

Show:

- raw chat not stored
- PII redacted count
- media skipped count
- deleted messages skipped count
- prompt injection events
- captured events count
- needs review count

## Copy style

Use simple language.

Examples:

```text
Analyze Memories
Captured Memories
Needs Review
Raw chat is not stored
Media messages skipped
Draft message
Find flowers
Send e-card
```

## Do not build

- real WhatsApp sending
- real marketplace checkout
- real Yelp integration
- image analysis
- family/friend grouping
