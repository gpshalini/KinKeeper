# KinKeeper Product Requirements

## MVP summary

KinKeeper analyzes a user-uploaded or pasted WhatsApp-style text export and automatically captures likely birthdays, anniversaries, and remembrance dates into one upcoming memories list.

Each captured event includes:

- person name as found in the chat
- event type
- inferred date
- confidence
- source snippet
- reminder timing
- suggested next action
- edit option
- delete option
- audit log entry

## User experience decisions

KinKeeper should:

- auto-capture likely events
- avoid mandatory confirmation for every event
- allow users to edit later
- allow users to delete incorrect events
- use one unified event list
- avoid family/friend grouping
- save unknown people as `Unknown person`
- preserve names as they appear in the chat
- skip media analysis for MVP
- show mock gift or e-card actions without enabling real transactions

## TDD and security planning requirements

Before building product logic, write a short planning gate covering:

- what could go wrong in chat parsing and event extraction
- what private data is protected
- edge cases from WhatsApp exports
- tests required before marking the feature complete
- security checks required before saving any event

Minimum edge cases to plan for:

- multiline messages
- media omitted
- deleted messages
- phone-number senders
- generic birthday without a name
- repeated birthday wishes
- birthday wishes across two dates
- holidays that should be ignored
- prompt injection text inside chat content

## Input

Supported for MVP:

- `.txt` WhatsApp-style export
- pasted chat text
- synthetic mock WhatsApp export

Not supported for MVP:

- live WhatsApp connection
- image OCR
- video analysis
- audio analysis
- sticker analysis
- real marketplace checkout
- auto-send messaging

## WhatsApp parsing patterns

Support messages like:

```text
[9/30/24, 12:20:54 PM] Emily: Happy birthday Olivia 🎂
```

Support multiline messages:

```text
[9/30/24, 1:25:32 PM] +1 (555) 123-4567: Happy birthday Olivia,
Wishing you good health and happiness.
```

If a line does not start with a timestamp, treat it as continuation of the previous message.

## Messages to skip

Skip and log as unsupported or ignored:

```text
image omitted
GIF omitted
video omitted
audio omitted
sticker omitted
This message was deleted.
Messages and calls are end-to-end encrypted.
created this group
added
changed the subject
```

## Event detection

Detect:

- `happy birthday`
- `happy bday`
- `birthday wishes`
- `many many happy returns`
- `happy anniversary`
- `wedding anniversary`
- `remembering`
- `remembrance`
- `death anniversary`
- `we miss him`
- `we miss her`

Ignore for MVP unless paired with a person and event date:

- Happy New Year
- Merry Christmas
- Happy Diwali
- Happy Thanksgiving
- Congratulations
- Happy journey
- Safe travels
- Generic URLs

## Name extraction rules

Use the name as it appears in the message.

Examples:

```text
Happy birthday Uncle Robert
Person: Uncle Robert
```

```text
Happy anniversary Lisa and David
Person: Lisa and David
```

```text
Happy birthday!
Person: Unknown person
Confidence: Low
```

Do not blindly use the sender as the event person unless the message clearly indicates the sender is being wished through replies like `thank you everyone` after a cluster. For MVP, keep this conservative.

## Date inference

Use the message date as the likely event date.

For repeated wishes:

```text
Same person + same event type + within 2 days = one event
```

Use the earliest high-confidence date in the cluster as the event date.

## Confidence rules

High confidence:

- explicit event phrase
- explicit person name
- clear date from timestamp

Medium confidence:

- event phrase with partial or nickname-style person name

Low confidence:

- event phrase with no person name
- ambiguous message
- generic birthday wish

## Event statuses

Use:

```text
captured
needs_review
edited
deleted
```

Do not use mandatory `confirmed` status in MVP.

## Reminder defaults

For every captured event:

- 7 days before
- 1 day before
- day of event

## Suggested actions

Show these actions as mock or disabled buttons:

- Draft message
- Send e-card
- Find flowers
- Reminder to call

No real sending, purchasing, or external marketplace API calls in MVP.

## Synthetic sample file

Create:

```text
data/sample_whatsapp_export.txt
```

The sample must use American names and include:

- clear birthday with name
- repeated birthday wishes
- birthday across two days
- anniversary for two people
- remembrance day
- generic birthday with no name
- phone number sender
- media omitted
- deleted message
- edited message marker
- holiday greeting to ignore
- URL to ignore
- prompt injection attempt to ignore
- multiline birthday message

Never use real names or messages from private exports.

## Generated storage files

Create:

```text
data/confirmed_events.example.json
```

Use synthetic example data only.

The actual runtime may write to:

```text
artifacts/events.json
artifacts/audit_log.jsonl
```

Do not store raw chat text in artifacts.
