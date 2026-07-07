# KinKeeper Build System

Read this file first.

This folder contains the modular build instructions for KinKeeper, a Kaggle Vibe Coding Agents Capstone project.

## What to do in Antigravity

Open this exact folder in Antigravity:

```text
/Users/shaliniguda213/Desktop/Kaggle BootCamp_SGP/KinKeeper
```

Do not open the Desktop.
Do not open the parent `Kaggle BootCamp_SGP` folder.
Open the `KinKeeper` folder itself.

Then start the build with:

```text
@00_START_HERE.md start
```

## Instruction to Antigravity

When this file is referenced with `start`, do the following:

1. Read `03_BUILD_ORCHESTRATOR.md`.
2. Follow the phases exactly.
3. Read only the files needed for the current phase.
4. Pause after each phase and wait for user approval.
5. Do not build everything in one uncontrolled pass.
6. Do not run automated browser UI testing or repeated LLM integration tests.
7. Keep responses short. Report only what changed, result, and next step.
8. Never include API keys, passwords, real WhatsApp exports, or private family data in code or docs.
9. Use only synthetic sample data in the GitHub-ready project.
10. Apply the TDD and security planning gate before implementing each major feature.

## Folder purpose

The root markdown files define product, architecture, security, UI, tests, visuals, and submission requirements.

The `.agents` folder defines Antigravity project rules and reusable skills.

The `specs` folder contains Gherkin-style behavior specs used for spec-driven development.

## Build style

This project should demonstrate:

- ADK multi-agent system
- ADK workflow graph
- MCP server and MCP tools
- Agent skills
- Security and privacy controls
- Lightweight observability
- TDD planning gates
- Gherkin specs
- Evaluations and tests
- Functional UI
- Visual architecture assets
- README and capstone submission docs

## Output expectation

The final generated project should be a working local-first prototype that can be run, tested, documented, and shown in a 3 to 4 minute demo video.
