# KinKeeper Deployability Notes

KinKeeper is local-first by design because it processes private family chat exports. The codebase is fully prepared for local execution, development, testing, and playgrounds.

## Local-First Philosophy
*   **Privacy Control:** Running the UI locally on `http://127.0.0.1:8000/ui` keeps raw WhatsApp exports from leaving the user's computer.
*   **Sandbox Safety:** The application uses sandbox constraints (restricting file reads to `data/` and disabling outbound messaging integrations) to guarantee that no auto-sends or purchases can occur.

## Production Roadmap (Optional)
If public deployment is desired in the future, the following layers are recommended:
1.  **Transport Security (TLS/HTTPS):** Run FastAPI behind a reverse proxy (like Nginx) with SSL certificates.
2.  **Authentication:** Integrate Firebase Auth or OAuth2 middleware before exposing the `/ui` or `/api/` endpoints.
3.  **Encrypted Storage:** Encrypt the database `events.json` at rest using envelope encryption (e.g., KMS).
