---
name: what-did-i-forget
description: Accountability audit skill — scans Granola meeting notes, Google Calendar (via gcalcli), and Slack to surface commitments made but not acted on, decisions with no follow-through, and people waiting on you. Use this skill whenever the user asks what they've forgotten, what they owe people, what's slipping through the cracks, who's waiting on them, or wants a weekly/daily accountability check. Also trigger when the user says things like "catch me up", "what did I miss", "what do I owe", "run a check", or "what-did-i-forget". Outputs a ranked markdown report with draft messages for urgent items.
---

# What Did I Forget?

Audits Granola, Calendar, and Slack to surface forgotten commitments, open threads, and underprepared meetings. Sends results as a Slack DM to U0A1QFLEX2N and saves to `/Users/lornapurcell/Desktop/classdojo-districts/forgot-check-YYYY-MM-DD.md`.

**Parameters:** `days` (default 14), `focus` (optional person/project filter)

## Step 1: Granola
Call `query_granola_meetings` asking for: commitments I made, decisions, open threads, and action items from the last `days` days. Tag each item with date and person involved.

Commitment signals: "I'll", "I will", "let me", "Lorna will", "can you" + a specific deliverable.

## Step 2: Google Calendar
Use the Google Calendar MCP to list events from today through end of this week. Flag meetings where a Granola commitment involves an attendee (natural follow-up window) or where you're underprepared.

## Step 3: Slack
Search with `slack_search_public_and_private` for: `@me` (unresolved asks) and `from:me "I'll" OR "follow up" OR "let me check"` (promises you made). Prioritize anything where the person followed up again after your message.

## Step 4: Report & Send

Output structure (keep it tight — scannable in 30 seconds):
- 🔴 **Overdue/At-Risk** — specific deliverable, who's waiting, age
- 🟡 **Decisions not acted on**
- 📅 **This week's meetings — underprepared**
- 🧵 **Lower priority open threads**

Rank by: meeting proximity this week > DM follow-up > age > channel mention.

Send as Slack DM to U0A1QFLEX2N. If any source fails, note it and continue.
