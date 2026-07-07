---
name: stride-threat-model
description: Use this skill when creating a STRIDE threat model for KinKeeper or reviewing security risks in an agentic workflow.
---

# STRIDE Threat Model Skill

## Purpose

Create a concise STRIDE threat model for KinKeeper.

## STRIDE categories

### Spoofing

Ask:

- Can a sender or event identity be misinterpreted?
- Can a malicious message pretend to be an instruction?

### Tampering

Ask:

- Can event records be modified without user visibility?
- Can saved artifacts be manipulated?

### Repudiation

Ask:

- Are edit/delete actions logged?
- Can the system explain why an event was captured?

### Information disclosure

Ask:

- Can raw chat leak?
- Can phone numbers or emails appear in saved snippets?
- Can `.env` be read?

### Denial of service

Ask:

- Can a huge chat export overload local processing?
- Are file size limits enforced?

### Elevation of privilege

Ask:

- Can chat text cause the agent to use tools it should not?
- Can the MCP server read forbidden paths?
- Can the app perform real external actions?

## Required output

Create:

```text
docs/threat_model.md
```

Include:

- threat
- impact
- mitigation
- implementation file reference
- residual risk

## KinKeeper-specific controls

- no raw chat storage
- PII redaction
- prompt injection detection
- private path blocking
- no `.env` reads
- no auto-send
- no purchases
- audit log
- edit/delete capability
