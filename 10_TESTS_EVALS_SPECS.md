# Tests, Evaluations, and Specs

## Goal

Show that KinKeeper was not only vibe-coded. It should have behavior specs, TDD planning gates, tests, and lightweight evals.

## TDD planning gate

Before implementation, define tests for each major feature.

For every major feature, document:

| Feature | What could go wrong | Protected item | Edge cases | Required tests |
|---|---|---|---|---|

Use this table in implementation notes, docs, or the README.

Minimum required rows:

| Feature | What could go wrong | Protected item | Edge cases | Required tests |
|---|---|---|---|---|
| WhatsApp parser | Multiline messages are split incorrectly | Message structure | media omitted, deleted messages, phone number senders | parser tests |
| Event extraction | Wrong person is captured | Event accuracy | generic happy birthday, nicknames, repeated wishes | extraction evals |
| Duplicate merge | Same birthday appears as multiple cards | Reminder quality | same person across two dates | duplicate merge tests |
| Privacy guard | Phone number leaks into saved output | PII | phone sender, phone in message body | redaction tests |
| MCP file reader | Tool reads private files | Local files and secrets | `.env`, data/private, large files | MCP security tests |
| Suggested actions | App appears to send or buy something | User consent | flower button, e-card button | mock-action tests |
| UI display | UI shows raw chat or unredacted snippet | Private chat content | long snippets, phone numbers, prompt injection | UI/privacy tests |

## Files to create

Generated project should include:

```text
specs/kinkeeper.feature
tests/test_parser.py
tests/test_event_extraction.py
tests/test_privacy.py
tests/test_mcp_tools.py
tests/test_ui_flow.py
evals/test_cases.json
evals/run_evals.py
evals/sample_eval_results.md
```

## Gherkin scenarios

Use `specs/kinkeeper.feature` as the source of behavior expectations.

Include scenarios for:

1. clear birthday with name
2. repeated birthday wishes merged
3. birthday across two days merged
4. anniversary with two names
5. remembrance day captured
6. generic birthday without name marked needs review
7. media omitted skipped
8. deleted message skipped
9. prompt injection ignored
10. phone number redacted
11. holiday greeting ignored
12. raw chat not stored

## Unit tests

### Parser tests

Verify:

- timestamp parsing
- sender parsing
- multiline message merging
- media omitted detection
- deleted message detection
- system message skipping

### Event extraction tests

Verify:

- birthday detection
- anniversary detection
- remembrance detection
- unknown person handling
- duplicate merge logic
- confidence assignment

### Privacy tests

Verify:

- phone number redaction
- email redaction
- prompt injection detection
- raw chat not saved

### MCP tests

Verify:

- sample file can be read
- private paths are rejected
- `.env` cannot be read
- events are saved as structured JSON
- audit log writes JSON lines
- mock suggestions do not call external APIs

## Evaluation cases

Create `evals/test_cases.json` with 8 to 12 cases.

Each case should include:

```json
{
  "id": "clear_birthday",
  "input": "...",
  "expected": {
    "event_type": "birthday",
    "person": "Olivia",
    "confidence": "high",
    "status": "captured"
  }
}
```

## Evaluation scoring

The eval runner should check:

- event type match
- person extraction
- date inference
- confidence
- status
- PII redaction
- skip behavior
- duplicate merge behavior

Use simple deterministic scoring.

Example output:

```text
10/12 cases passed
2 cases need review
```

## Manual playground tests

README should include 3 manual tests:

### Test 1: Clear birthday cluster

Expected:

- one birthday event
- high confidence
- duplicate messages merged

### Test 2: Ambiguous birthday

Expected:

- Unknown person
- low confidence
- needs_review

### Test 3: Prompt injection

Expected:

- no instruction followed
- security event logged
- normal extraction continues safely

## Test command

Add Makefile target:

```bash
make test
```

Add eval target:

```bash
make eval
```

## Acceptance criteria

Do not call the project complete unless:

- TDD planning gate is documented
- tests pass
- evals run
- sample results are documented
- README explains how to run tests and evals
