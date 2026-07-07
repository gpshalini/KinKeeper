# KinKeeper Security Model

KinKeeper enforces strict privacy-by-design principles to ensure sensitive family chat exports are never compromised.

## Key Security Pillars

1.  **PII Redaction:** The Privacy Guard node automatically masks phone numbers, addresses, and email addresses with standard tokens (e.g. `[PHONE_REDACTED]`) before saving snippets.
2.  **No Raw Chat Storage:** The raw chat logs are processed purely in-memory and discarded. Only final structured JSON events are persisted.
3.  **Local MCP Execution:** All file reads, database saves, and logging operations occur via the local MCP server running on the user's localhost machine.
4.  **No Auto-Send Boundary:** KinKeeper generates draft messages and suggestions but provides NO auto-send or purchase integration. The user remains in complete control.
5.  **No Environment Key Leakage:** `.env` keys are loaded locally and are never returned through FastAPI API responses or logs.
