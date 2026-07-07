# KinKeeper Project Brief

## Project name

KinKeeper

## Capstone track

Primary track: Concierge Agents

Secondary angle: Agents for Good

## One-line description

KinKeeper is a privacy-safe family memory concierge agent that turns WhatsApp-style chat exports into an auto-captured list of birthdays, anniversaries, and remembrance dates.

## Problem

Important family dates often live inside noisy group chats or in one person’s memory. Birthdays, anniversaries, remembrance days, and family milestones can get lost across messages, media, time zones, and repeated wishes.

KinKeeper helps preserve these memories without requiring a live WhatsApp connection, manual spreadsheet tracking, or family members confirming each event one by one.

## Target user

A person who is part of family or friend group chats and wants a lightweight way to remember important dates from past messages.

## MVP value

The user uploads or pastes a WhatsApp-style text export. KinKeeper extracts likely memories, auto-captures them into a single upcoming memories list, and lets the user edit or delete later.

## MVP input

- WhatsApp-style text export
- Demo uses a synthetic mock export with American names
- Real user exports are local-only and must never be committed to GitHub
- Media files are not analyzed in the MVP

## MVP output

A single upcoming memories list with:

- Person name as found in chat
- Event type
- Inferred date
- Confidence
- Source snippet
- Reminder timing
- Suggested next action
- Edit and delete options
- Lightweight privacy audit trail

## Event types

KinKeeper should detect:

- Birthday
- Anniversary
- Remembrance day
- Death anniversary

KinKeeper should ignore for MVP:

- Generic holiday greetings
- Travel wishes
- General congratulations
- Links without event context
- Media-only messages

## Key product decisions

- No family/friend grouping
- No mandatory confirmation gate
- Auto-capture likely events
- User can edit or delete later
- Keep one clean upcoming memories list
- Save only structured event data
- Do not store raw chat text
- Do not send messages
- Do not make purchases
- Gift and e-card buttons are mock or disabled for demo

## Future roadmap

- Image greeting detection
- OCR on greeting cards
- Live WhatsApp export import flow
- Calendar sync
- Real local marketplace integration
- E-card or flower vendor integrations
- Relationship-aware categorization
