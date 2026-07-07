# Visual Assets

## Goal

Create final visual assets after the architecture and code are stable.

Do not generate final diagrams before the agent architecture is finalized.

## Global visual direction

All generated visuals must be pastel themed, elegant, warm, and modern.

Use:

- soft cream, blush, sage, lavender, dusty blue, pale peach, warm beige, and soft gold accents
- clean white or light neutral backgrounds
- elegant rounded cards
- subtle shadows
- airy spacing
- refined typography
- calm family-memory feeling
- polished product-submission quality

Avoid:

- dark navy backgrounds
- neon glow
- hacker aesthetic
- harsh gradients
- overly corporate dashboards
- cluttered diagram layouts
- childish cartoon styling
- black background unless the user explicitly asks later

The visual identity should feel like:

```text
private family memory + elegant AI assistant + calm reminder app
```

If diagrams need contrast, use soft outlines, muted accent colors, and clean labels instead of dark backgrounds or neon effects.

## Assets folder

Generated project should include:

```text
assets/
  cover_banner.png
  architecture_diagram.png
  process_flow_diagram.png
  agent_graph_diagram.png
```

UI mockups are optional and should not be generated first.

## 1. Cover banner

File:

```text
assets/cover_banner.png
```

Purpose:

Use in README and capstone submission.

Prompt direction:

```text
Premium pastel project cover banner for KinKeeper. Large title: KinKeeper. Subtitle: Privacy-safe family memory concierge. Visual theme: family memory, calendar reminders, private AI assistant, soft cream background, blush and sage accents, subtle lavender and dusty blue details, elegant rounded shapes, modern clean layout. Include subtle icons for chat, calendar, privacy, and reminders. 16:9 landscape.
```

## 2. Architecture diagram

File:

```text
assets/architecture_diagram.png
```

Must show:

- Local UI
- ADK orchestrator
- specialized agents
- MCP server
- local storage artifacts
- security checkpoint
- audit log
- no raw chat storage
- mock suggestions only

Diagram content:

```text
User
 -> Local UI
 -> ADK Orchestrator
 -> Chat Parser Agent
 -> Event Extraction Agent
 -> Privacy Guard Agent
 -> Reminder Planner Agent
 -> Message and Gift Concierge Agent
 -> Audit Report Agent
 -> Final UI response
```

MCP side panel:

```text
Local MCP Server
- read_sample_chat_export
- save_captured_events
- list_captured_events
- generate_reminder_schedule
- suggest_demo_actions
- write_audit_log
```

## 3. Process flow diagram

File:

```text
assets/process_flow_diagram.png
```

Must show product flow:

```text
Upload or paste chat export
 -> Parse messages
 -> Skip media/deleted/system messages
 -> Detect events
 -> Merge duplicates
 -> Redact PII
 -> Auto-capture structured events
 -> Show upcoming memories
 -> Edit or delete
 -> Generate reminder and mock action suggestions
 -> Show audit summary
```

## 4. Agent graph diagram

File:

```text
assets/agent_graph_diagram.png
```

Must show:

- workflow graph nodes
- routing
- security checkpoint
- MCP tools connected to relevant agents
- audit log output

Highlight:

- Privacy Guard Agent
- Security checkpoint
- MCP server
- no auto-send and no purchase boundary

## Visual style

For technical diagrams:

- light pastel or clean white background is preferred
- professional capstone feel
- readable labels
- no clutter
- use actual agent and tool names from code
- diagrams must match implementation

For cover banner:

- pastel, elegant, warm, and human
- not too corporate
- not dark
- should feel like private family memory plus AI
- use soft, premium visual treatment

## README requirement

Embed all generated visuals in README under:

```markdown
## Visual Assets
```

## Demo requirement

The demo script should reference:

- cover banner
- architecture diagram
- process flow or agent graph
