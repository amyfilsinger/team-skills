---
name: qbr-monitoring
description: Track ClassDojo DPM team impact review (QBR) progress against quarterly goals by pulling calendar data across the team. Use this whenever the user asks about impact review counts, QBR pacing, how many impact reviews have been completed, who's behind on reviews, progress toward the 138-review quarterly goal, or anything that sounds like "how is the team tracking on QBRs/impact reviews." Also trigger for questions like "how many reviews has Sophie done?", "are we on pace for Q2?", "show me impact review counts by DPM", or "who has the most/fewest reviews this quarter." DPMs covered: Sophie Kronk, Andrew Menegat, Dillon Jack, Jackson Shaad, Ashley Green.
---

# QBR Monitoring

Pull each DPM's external impact review meetings from Google Calendar and report progress against the quarterly target.

## Team and target

**DPM calendars to query:**
| Name | Calendar ID |
|---|---|
| Sophie Kronk | `sophie.kronk@classdojo.com` |
| Andrew Menegat | `andrew.menegat@classdojo.com` |
| Dillon Jack | `dillon.jack@classdojo.com` |
| Jackson Shaad | `jackson.shaad@classdojo.com` |
| Ashley Green | `ashley.green@classdojo.com` |

**Quarterly target:** 138 impact reviews total across the team  
**Q2 start date:** April 1, 2026

## What counts as an impact review

A calendar event counts if **both** conditions are true:

1. **Title contains an impact-review keyword** (case-insensitive): "impact", "impact review", "qbr", "quarterly business review"
2. **External meeting**: at least one attendee whose email is NOT `@classdojo.com`

An internal-only meeting (all @classdojo.com) does not count even if "impact" is in the title. Training sessions, planning calls, and internal syncs don't count.

## Workflow

### Step 1 — Query each calendar

Use `list_events` for each DPM calendar with:
- `calendarId`: the DPM's email (see table above)
- `startTime`: `2026-04-01T00:00:00`
- `endTime`: today's date (ISO format)
- `fullText`: `"impact"` (catches most variations; you'll verify title in Step 2)
- `pageSize`: 250

Run all 5 queries in parallel (one per DPM) to save time.

If a calendar returns a permission error (403/404), note it in the report as "access unavailable" rather than blocking — Amy may not have view access to all team calendars.

### Step 2 — Filter to qualifying events

For each event returned:
- **Title check**: the event `summary` must contain "impact", "qbr", or "quarterly business review" (case-insensitive)
- **External check**: the event must have at least one attendee whose email does not end in `@classdojo.com`
- **Date check**: event start must be ≥ 2026-04-01 (sanity-check, since the query already filters this)

Keep a list of qualifying events per DPM. If you're unsure about an edge case (e.g., a meeting with a vendor but titled "Impact Planning"), lean toward including it and note it.

### Step 3 — Build the report

Output a markdown table followed by a short status line:

```markdown
## DPM Impact Review Progress — Q2 2026 (as of [today])

| DPM | Reviews Completed | % of Individual Target |
|---|---|---|
| Sophie Kronk | X | X% |
| Andrew Menegat | X | X% |
| Dillon Jack | X | X% |
| Jackson Shaad | X | X% |
| Ashley Green | X | X% |
| **TOTAL** | **X** | **X% of 138** |

_Target: 138 reviews by end of Q2. Scanned [date range]. [Any access issues noted here.]_
```

**Individual target**: divide 138 evenly across the 5 DPMs = **27.6 per DPM** (round to 28 for display purposes). Show each DPM's count as a % of 28.

**Pace line**: After the table, add one sentence on whether the team is ahead or behind pace. To calculate expected pace: `(days elapsed since Apr 1) / (total Q2 days) × 138`. If total is within 10% of pace, call it "on pace." More than 10% behind = "behind pace." More than 10% ahead = "ahead of pace."

### Step 4 — Optionally list meetings

If the user asks for details ("show me the list", "which ones count"), append a collapsible section per DPM listing the qualifying meetings: date, district name (from the event title), and duration.

## Notes on access

Amy's Google Calendar credentials (via the calendar MCP) may or may not have read access to teammates' calendars. If a DPM's calendar returns no results:
1. First check if the query returned 0 events or an error — 0 events might just mean no qualifying meetings yet, which is different from an access error.
2. If it's an access error, note it clearly: "Jackson Shaad — calendar access unavailable; check with IT or ask Jackson to share."
3. Don't silently skip — the user needs to know if a DPM's data is missing from the total.
