# KinKeeper Build Orchestrator

You are an expert ADK agent builder working in Antigravity.

Follow this file phase by phase. Do not skip phases. Do not build everything at once.

## Global rules

- Work one phase at a time.
- Read only the referenced file for the current phase.
- Pause after each phase and ask the user before continuing.
- Keep responses concise.
- Do not show full file contents unless asked.
- Do not run automated browser UI testing or repeated LLM calls.
- Do not use real WhatsApp data in generated repo files.
- Use synthetic sample data only.
- Never write API keys or secrets into code.
- Keep all final implementation specific to KinKeeper.

## Mandatory TDD and security planning gate

Before implementing any major feature, write a short implementation plan with these sections:

1. What could go wrong?
2. What data, files, or actions are protected?
3. What edge cases must be handled?
4. What tests or evals must prove this works?
5. What security or privacy checks must pass?

Do not write implementation code for that feature until this planning gate is complete.

For KinKeeper, every feature must consider:

- raw chat should not be stored
- phone numbers and emails must be redacted
- prompt injection must be ignored
- media-only messages should be skipped
- deleted messages should be skipped
- low-confidence events should be marked `needs_review`
- no messages should be sent automatically
- no purchases or external marketplace actions should run
- `.env` must never be read or exposed
- private export paths should be rejected by default

## Required planning output format

For each major feature, include this before coding:

```markdown
### TDD and Security Planning Gate: <feature name>

**What could go wrong**
- ...

**What is protected**
- ...

**Edge cases**
- ...

**Tests and evals required**
- ...

**Security and privacy checks**
- ...
```

Keep this short and practical. Do not turn it into a long essay.

## Phase 0: Read context

Read these files first:

1. `01_PROJECT_BRIEF.md`
2. `02_CAPSTONE_RUBRIC_MAPPING.md`

Then summarize in five bullets:

- project name
- user problem
- core MVP
- capstone concepts
- key safety constraints

Pause and ask: Ready to continue to setup?

## Phase 1: Tech setup

Read:

- `04_TECH_SETUP.md`

Do the checks and setup described there.

Pause after setup.

## Phase 2: Product requirements and sample data

Read:

- `05_PRODUCT_REQUIREMENTS.md`

Before generating sample data or product models, apply the TDD and security planning gate for the parser and event extraction scope.

Create the required project data folder and synthetic sample WhatsApp file only when instructed by that file.

Pause after generating sample data and product model.

## Phase 3: ADK architecture

Read:

- `06_ADK_ARCHITECTURE.md`

Before writing agent code, apply the TDD and security planning gate for the ADK workflow graph and agent routing.

Build the ADK multi-agent workflow using Agents CLI scaffold and generated code.

Pause after core agent architecture exists.

## Phase 4: MCP tools

Read:

- `07_MCP_TOOLS.md`

Before writing MCP code, apply the TDD and security planning gate for file access, persistence, and tool permissions.

Build the local MCP server and wire MCP tools into relevant agents.

Pause after MCP tools are implemented.

## Phase 5: Security, privacy, observability

Read:

- `08_SECURITY_PRIVACY_OBSERVABILITY.md`

Before implementing security code, apply the TDD and security planning gate for PII redaction, prompt injection, audit logging, and raw chat protection.

Add security checkpoint, privacy rules, prompt injection detection, and audit logging.

Pause after security features are implemented.

## Phase 6: UI

Read:

- `09_UI_REQUIREMENTS.md`

Before building UI, apply the TDD and security planning gate for user inputs, editing/deleting, and privacy audit display.

Build a functional local UI. Prioritize working flow over visual polish.

Pause after UI is working locally.

## Phase 7: Specs, tests, evals

Read:

- `10_TESTS_EVALS_SPECS.md`
- `specs/kinkeeper.feature`

Create tests and eval artifacts.

Pause after tests run successfully.

## Phase 8: Visual assets

Read:

- `11_VISUAL_ASSETS.md`

Create final visuals after architecture is stable.

Pause after assets are created.

## Phase 9: Docs and submission

Read:

- `12_DOCS_SUBMISSION_DEMO.md`

Create README, submission writeup, demo script, GitHub instructions, and deployability notes.

Pause after final documentation is complete.

## Completion criteria

Do not declare completion until:

- ADK playground or local app runs
- UI can process sample mock WhatsApp export
- events are auto-captured
- edit and delete actions work
- no raw chat is stored
- security audit log is produced
- TDD planning gate appears in docs or implementation notes
- tests/evals exist
- README exists
- demo script exists
- visual assets exist
