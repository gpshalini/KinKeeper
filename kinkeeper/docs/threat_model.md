# KinKeeper STRIDE Threat Model

This document maps potential system threats using the STRIDE framework and documents the specific mitigations implemented in code.

| Threat Category | Potential Threat | Mitigation | Implementation Location |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Unauthenticated user accesses the dashboard | Dashboard runs on `localhost` (127.0.0.1) only, preventing external exposure. | [fast_api_app.py](file:///Users/shaliniguda213/Desktop/Kaggle%20BootCamp_SGP/KinKeeper/kinkeeper/app/fast_api_app.py) |
| **Tampering** | Prompt injection manipulates event extraction | Security checkpoint checks input using regex, stripping injection phrases completely. | [agent.py](file:///Users/shaliniguda213/Desktop/Kaggle%20BootCamp_SGP/KinKeeper/kinkeeper/app/agent.py#L37-L83) |
| **Repudiation** | Actions occur without tracking | Structured audit logs record all workflow runs, skips, and redactions. | [audit_log.jsonl](file:///Users/shaliniguda213/Desktop/Kaggle%20BootCamp_SGP/KinKeeper/kinkeeper/artifacts/audit_log.jsonl) |
| **Information Disclosure** | PII (phone/email) leaks to external APIs or database | PII is actively redacted from all persisted snippets and names. | [privacy_utils.py](file:///Users/shaliniguda213/Desktop/Kaggle%20BootCamp_SGP/KinKeeper/kinkeeper/app/privacy_utils.py) |
| **Denial of Service** | Giant chat log exhausts memory OR Gemini API 429 quota exhaustion blocks UI | Parser streams lines and limits buffer sizes; Endpoint rescues 429 errors and runs local regex fallback extractor. | [agent.py](file:///Users/shaliniguda213/Desktop/Kaggle%20BootCamp_SGP/KinKeeper/kinkeeper/app/agent.py#L86-L197), [fast_api_app.py](file:///Users/shaliniguda213/Desktop/Kaggle%20BootCamp_SGP/KinKeeper/kinkeeper/app/fast_api_app.py) |
| **Elevation of Privilege** | Path traversal tool reads `.env` or system secrets | MCP tool restricts paths to the current workspace `data` folder. | [mcp_server.py](file:///Users/shaliniguda213/Desktop/Kaggle%20BootCamp_SGP/KinKeeper/kinkeeper/app/mcp_server.py#L19-L27) |
