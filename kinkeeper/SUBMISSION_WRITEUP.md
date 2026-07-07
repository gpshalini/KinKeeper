# KinKeeper: Privacy-Safe Family Memory Concierge

## Abstract
KinKeeper is a privacy-first AI system designed to turn raw, unstructured WhatsApp chat logs into structured family milestone event registries and reminders (birthdays, anniversaries, and remembrance days). Built on the Google Agent Development Kit (ADK) and the Model Context Protocol (MCP), KinKeeper uses a 3-agent pipeline coupled with deterministic security sanitization and local filesystem storage. By running locally, KinKeeper guarantees that raw personal chats are never saved or exposed, ensuring absolute privacy for family memories.

## Problem Statement
Messaging platforms like WhatsApp are filled with important milestone announcements and wishes. However, these dates are easily buried and forgotten. Standard calendar applications require tedious manual entry, while cloud-based AI tools threaten personal privacy by requiring the upload of raw, sensitive chat histories (containing phone numbers, addresses, and highly private exchanges) to remote databases. 

## The Solution
KinKeeper automates the entire extraction pipeline without compromising user privacy. It offers a local FastAPI and HTML5 user dashboard where users can upload or paste chat logs. A secure orchestrator sanitizes inputs, skips system noise/media, redacts personally identifiable information (PII) like phone numbers and email addresses, merges duplicate wishes across dates, plans structured reminder cadences, and logs statistics in a structured audit trail—all completely local.

## ADK Multi-Agent System Design
KinKeeper implements a collaborative 3-agent pipeline:
1.  **Event Extractor Agent (`event_extractor`):** Uses an LLM to scan sanitized, parsed chat entries and flag milestones with metadata.
2.  **Identity Resolver Agent (`identity_resolver`):** Normalizes nicknames to standardized names (e.g. `Liv` -> `Olivia`) and semantically merges duplicates.
3.  **Creative Concierge Agent (`creative_concierge`):** Crafts customized, warm greeting drafts and suggests next steps (e.g., Send E-Card, Send Flowers).

## MCP Server Design
The local Model Context Protocol (MCP) server runs at `app/mcp_server.py`. It implements 6 tools to handle all filesystem operations:
*   `read_sample_chat_export`: Reads WhatsApp logs securely from a restricted directory.
*   `save_captured_events`: Saves structured events to a local JSON database.
*   `list_captured_events`: Returns saved events to the dashboard.
*   `generate_reminder_schedule`: Calculates calendar reminders.
*   `suggest_demo_actions`: Recommends context-aware mock actions.
*   `write_audit_log`: Appends records to the JSONL audit trail.

## Security & Privacy Design
*   **Prompt Injection Check:** Strips adversarial prompts (e.g., *"ignore previous instructions"*) before parser execution.
*   **PII Masking:** Replaces phone numbers and email addresses with redaction tokens.
*   **No Auto-Send Boundary:** Action buttons are interactive placeholders only, maintaining absolute human control.
*   **Directory Sandboxing:** Restricts MCP file reads to the workspace directory.

## Testing & Evaluations
*   **Gherkin Specs:** 11 scenarios in `specs/kinkeeper.feature` define the behavioral bounds.
*   **Unit & BDD Tests:** pytest-bdd step definitions and pytest unit tests achieve 100% test pass rates across parsing, privacy, and tools.
*   **Evals Suite:** The evaluations runner (`evals/run_evals.py`) runs 10 evaluation cases to check accuracy, PII redactions, and duplicate merging.
