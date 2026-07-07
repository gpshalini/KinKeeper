# UI Requirements

## Goal

Build a clean, functional local UI for KinKeeper.

Prioritize working functionality before visual polish.

Do not generate UI mockups before the functional UI exists. UI can be refined through live prompts later.

## UI purpose

The UI should let a user:

1. upload or paste a WhatsApp-style text export
2. analyze memories
3. see auto-captured events
4. edit or delete events
5. see reminder suggestions
6. see mock message, e-card, and flower actions
7. see privacy and audit summary

## TDD and security planning requirements

Before building UI, write a planning gate covering:

- what could go wrong with user input
- what private content is protected in the UI
- edge cases for empty files, invalid files, and parse errors
- tests required for upload/paste, edit/delete, and audit display
- security checks required before displaying snippets or suggestions

The UI must not display unredacted phone numbers, full raw chat, or private file paths.

## Required screens or sections

### 1. Home and input section

Include:

- KinKeeper title
- short product explanation
- privacy note
- upload `.txt` file option
- paste chat text option
- use demo sample button
- Analyze Memories button

Privacy note:

```text
KinKeeper only saves structured event records. Raw chat text is not stored.
```

### 2. Captured memories list

Display one unified list.

Each event card should show:

- person
- event type
- date
- confidence
- status
- redacted source snippet
- reminder timing
- suggested next action
- Edit button
- Delete button

No family/friend grouping.

### 3. Needs review section

Low-confidence or ambiguous events should be clearly marked.

Example:

```text
Unknown person
Birthday
Confidence: Low
Status: Needs review
```

### 4. Edit event panel

Allow user to edit:

- person
- event type
- date
- notes
- status

### 5. Suggested actions panel

Show demo-only actions:

- Draft message
- Send e-card
- Find flowers
- Reminder to call

Rules:

- Draft message may generate local text only
- E-card and flower buttons should be disabled or marked future
- No real external actions

### 6. Privacy audit panel

Show:

- raw chat not stored
- PII redacted count
- media skipped count
- deleted messages skipped count
- prompt injection detections
- captured event count
- needs review count

## Visual style direction

Default visual direction:

- pastel themed
- elegant and warm
- soft cream, blush, sage, lavender, dusty blue, pale peach, and warm beige
- clean cards
- rounded corners
- subtle shadows
- calm privacy-first feeling
- modern but not cold

Avoid dark hacker-style visuals, neon-heavy styling, black backgrounds, or dense enterprise dashboard design.

## Visual direction

Do not overdesign in the first pass.

Use:

- warm, trustworthy, calm style
- clean cards
- readable typography
- soft background
- clear primary actions
- privacy-forward messaging

Avoid:

- dark hacker style for the actual app UI
- complicated animations
- dense enterprise dashboard feel
- too many colors
- cluttered tables

## Suggested page layout

```text
Header
  KinKeeper
  Privacy-safe family memory concierge

Input card
  Upload / paste / use demo sample

Results area
  Captured memories cards

Side panel or lower section
  Suggested actions
  Privacy audit
```

## Empty states

Before analysis:

```text
Upload a WhatsApp-style chat export or use the demo sample to find important family memories.
```

No events found:

```text
No birthdays, anniversaries, or remembrance dates were found. Try another export or check that the messages include event wording.
```

Media skipped:

```text
Some media messages were skipped. Image-based greeting detection is planned for a future version.
```

## Error states

Show clear messages for:

- invalid file type
- empty file
- file too large
- no parseable WhatsApp messages
- unsafe private path
- failed analysis

## Accessibility

Use:

- readable font sizes
- sufficient contrast
- labels on buttons
- keyboard-friendly controls
- clear error messages
