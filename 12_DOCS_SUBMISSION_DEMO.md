# Docs, Submission, and Demo

## Goal

Create the final documentation and demo materials for the Kaggle capstone submission.

## Required files

Generated project should include:

```text
README.md
SUBMISSION_WRITEUP.md
DEMO_SCRIPT.txt
docs/architecture.md
docs/security_model.md
docs/threat_model.md
docs/deployability.md
.env.example
```

## README requirements

The README must include:

1. Project title
2. One-line description
3. Problem statement
4. Solution summary
5. Capstone concepts used
6. TDD and security planning gate summary
7. Architecture diagram
8. Process flow
9. Agent architecture
10. MCP tools
11. Security and privacy model
12. UI overview
13. Setup instructions
14. Run instructions
15. Test instructions
16. Eval instructions
17. Sample demo inputs
18. Troubleshooting
19. GitHub safety note
20. Deployability notes
21. Visual assets

## Quick start format

Include:

```bash
git clone <repo-url>
cd kinkeeper
cp .env.example .env
# add your GOOGLE_API_KEY
make install
make playground
```

Also include:

```bash
make test
make eval
make run
```

## `.env.example`

Create:

```text
GOOGLE_API_KEY=your_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=False
GEMINI_MODEL=gemini-2.5-flash
```

Never include a real API key.

## Submission writeup

`SUBMISSION_WRITEUP.md` should include:

- Abstract
- Problem
- Solution
- Why this matters
- Architecture
- ADK multi-agent design
- MCP server design
- Agent skills used
- TDD and security planning gate
- Security and privacy design
- Spec-driven development
- Evals and tests
- UI walkthrough
- Deployability
- Future roadmap

## Demo script

Create:

```text
DEMO_SCRIPT.txt
```

Length:

- 3 to 4 minutes
- first person
- clear and conversational
- no overtechnical explanation

Structure:

```text
0:00 Hook
0:20 What KinKeeper is
0:45 Show cover banner
1:00 Show architecture
1:30 Show live UI
2:15 Show captured memories
2:45 Show privacy audit
3:10 Show MCP, TDD planning, and tests
3:30 Close with impact
```

## Demo must show

- Antigravity project
- `.agents/skills`
- ADK agent code
- MCP server code
- TDD planning gate section
- sample WhatsApp export
- UI running locally
- captured events
- edit/delete option
- privacy audit
- tests or evals
- README and visuals

## Deployability notes

The project does not need a public endpoint.

Explain:

```text
KinKeeper is local-first by design because it may process private family chat exports. The README documents how to run it locally and includes optional deployment considerations, but public deployment is intentionally not required for the demo.
```

## GitHub push instructions

Include in README:

```bash
git init
git add .
git commit -m "Initial commit: KinKeeper ADK agent"
git branch -M main
git remote add origin https://github.com/<your-username>/kinkeeper.git
git push -u origin main
```

Before pushing, verify:

```bash
git status
git check-ignore .env
```

## Final safety checklist

Before final submission:

- `.env` is not committed
- only synthetic data is committed
- no real WhatsApp exports are included
- no API keys are included
- app runs locally
- TDD planning gate is documented
- tests pass
- evals run
- README is complete
- submission writeup is complete
- demo script is ready
- visuals are embedded
