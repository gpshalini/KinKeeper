# Capstone Rubric Mapping

This file maps KinKeeper to the Kaggle Vibe Coding Agents Capstone concepts.

## Required concepts

The capstone requires at least three key concepts. KinKeeper is designed to demonstrate more than six.

| Concept | Used? | Where it appears |
|---|---:|---|
| ADK agent or multi-agent system | Yes | `06_ADK_ARCHITECTURE.md`, generated `agent.py` |
| MCP server | Yes | `07_MCP_TOOLS.md`, generated `mcp_server.py` |
| Antigravity | Yes | Build and demo video |
| Security features | Yes | `08_SECURITY_PRIVACY_OBSERVABILITY.md`, generated security node |
| Deployability | Yes | README, Makefile, local run instructions |
| Agent skills | Yes | `.agents/skills/*/SKILL.md` |
| Spec-driven development | Yes | `specs/kinkeeper.feature` |
| TDD planning gate | Yes | `03_BUILD_ORCHESTRATOR.md`, `.agents/CONTEXT.md`, `10_TESTS_EVALS_SPECS.md` |
| Evaluations | Yes | tests and eval files generated from `10_TESTS_EVALS_SPECS.md` |
| Observability | Yes | structured audit log |
| UI | Yes | `09_UI_REQUIREMENTS.md` |

## Minimum visible concept set for judges

The final repo and video must make these obvious:

1. ADK multi-agent workflow
2. Custom MCP server and tools
3. Agent skills
4. Security and privacy controls
5. TDD planning gate
6. Spec-driven Gherkin scenarios
7. Tests and evaluations
8. Antigravity usage
9. Deployability through local reproducible setup

## Technical implementation expectations

The generated project should include:

- ADK workflow graph
- Orchestrator agent
- Specialized agents
- Tool use through MCP
- Domain-specific logic for WhatsApp-style chat parsing
- Auto-captured event records
- Edit and delete flow
- Structured audit logs
- PII redaction
- Prompt injection detection
- Synthetic sample data
- TDD plan artifacts or plan sections in generated docs
- README with setup instructions
- Submission writeup
- Demo script
- Visual assets

## Documentation expectations

The final GitHub submission should include:

- `README.md`
- `SUBMISSION_WRITEUP.md`
- `DEMO_SCRIPT.txt`
- Architecture diagram
- Process flow diagram
- Agent graph diagram
- Security model
- Sample test cases
- Setup and run instructions
- `.env.example`
- `.gitignore`

## Non-negotiables

- Never commit `.env`
- Never commit API keys
- Never commit real WhatsApp exports
- Never commit private family data
- Never send messages automatically
- Never make purchases
