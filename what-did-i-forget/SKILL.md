---
name: what-did-i-forget
description: Audit the user's recent meetings, calendar, and Slack to surface dropped commitments, unacted decisions, and underprepared upcoming meetings. Use this whenever the user asks "what am I forgetting", "what's slipping", "what do I owe people", "am I prepared for this week", "catch me up on loose ends", "what am I behind on", or any variation of checking for open loops across their tools — even if they don't explicitly mention Granola, Calendar, or Slack. Also trigger when the user says things like "forgot-check", "accountability check", or wants a weekly sweep of commitments. The skill pulls Granola meeting notes, cross-references Google Calendar, scans Slack DMs/mentions, and produces a ranked markdown report with draft follow-up messages.
---

# What Did I Forget

A cross-tool accountability audit. Pulls the user's own words and commitments out of meeting notes, then checks whether they've actually been acted on in Calendar and Slack.

## When this runs

The user wants to know what's slipping. That means: commitments they made that don't have time blocked, decisions reached in meetings that nobody's executing on, threads where someone is waiting on them, and meetings this week they're about to walk into cold.

The user probably can't keep this all in their head — that's the whole point of the skill. Your job is to do the cross-referencing they'd do if they had the time.

## Parameters

Accept these as arguments, with sensible defaults:

- **`days`** — how far back to scan Granola. Default: **14**. Shorter (3–7) for a quick pulse check; longer (30) for a deeper sweep.
- **`focus`** — optional filter. Can be a person's name, a project, a district, or a keyword. When set, filter meetings, Slack threads, and calendar events to that topic. Leave unset for a full sweep.

If the user gives natural-language hints ("last 3 days", "just Memphis stuff"), translate those into these parameters rather than asking them to restate.

## The workflow

### Step 1 — Pull Granola meeting notes

Use `list_meetings` with `time_range: "custom"` and the date range computed from `days`. This gets you the meeting IDs reliably even when the natural-language query endpoint is slow.

Then batch-fetch the notes with `get_meetings` (max 10 IDs per call — split into multiple calls if you have more meetings). The summaries and action items live in the returned content.

**Why not use `query_granola_meetings` directly?** It's the more convenient tool but it times out more often on wide date ranges. The list → get_meetings path is slower per call but far more reliable. If you want the convenience path, try `query_granola_meetings` first with a ≤30-second budget; fall back to list+get on timeout.

### Step 2 — Extract commitments, decisions, and open threads

Read each meeting's summary + action items. For each meeting, pull out:

- **Commitments the user made** — anything phrased as "Amy: [verb]", "I'll [verb]", "[user] to [verb]". Note the deadline if mentioned, else mark as "no deadline stated."
- **Decisions reached** — "we decided", "going with X", "approved", or any resolution that implies future action.
- **Open threads** — questions left hanging, things flagged for follow-up, items explicitly parked, unresolved debates.

Keep a running list in memory with: commitment text, meeting title, meeting date, who else is involved, and any deadline.

If `focus` is set, filter this list now.

### Step 3 — Check Google Calendar

Call `list_events` for the current week (today through end of week — you can go 7 days out if it's early in the week).

For each commitment from Step 2, check:

1. Is there a calendar event that looks like follow-through? (e.g., a meeting with the relevant person, a time block with the matching keyword, a 1:1 where it could plausibly be discussed)
2. Is there an upcoming meeting where the user owes an input they haven't delivered?

**Mark at-risk:** commitments with a real deadline or clear owner-is-waiting signal, no matching calendar event, and no evidence of recent action.

While you have the calendar loaded, also identify:

- **Kickoffs, external meetings, and new-relationship meetings this week** — these are "prep stakes high" by default.
- **Meetings where the user owes a deliverable** — e.g., a dashboard review where they committed an input, a WBR where they're presenting.

### Step 4 — Check Slack

Search Slack for things the user said they'd do and haven't followed up on. Two searches matter most:

- `from:me after:YYYY-MM-DD` to see what the user has been sending — scan for "I'll send", "let me check", "I'll circle back", "following up", or unresolved questions the user was supposed to answer.
- `to:me` / mentions to see what's queued up waiting for a reply.

For DMs, threads where the user sent the last message that promised something — and where the counterparty hasn't received what was promised — are high-signal. Threads where someone else is waiting on the user's response are also high-signal.

Cross-reference Slack threads against the commitments list. If someone is explicitly waiting on a commitment from Step 2, upgrade its urgency.

**If `focus` is set:** narrow the Slack search to channels or people matching the focus.

### Step 5 — Rank and produce the report

Produce a markdown report with this exact structure:

```markdown
# What I'm Forgetting — [date]

_Scanned the last [N] days of Granola, this week's calendar, and recent Slack activity._

## 1. Things I owe people — overdue or at-risk

🔴 High urgency / 🟡 Medium urgency — one bullet each, in this form:

- **[Commitment title]** — [who is waiting, what's the deadline or context]
  - Source: [Meeting title, date] / [Slack thread permalink]
  - Why it's at risk: [no calendar event / past deadline / someone explicitly asked for it]

## 2. Decisions made but not acted on

| Decision | Source meeting | What's needed next |
|---|---|---|
| ... | ... | ... |

## 3. This week's meetings where I'm underprepared

🔴 for external kickoffs / first-time stakeholder meetings with no prep doc.
🟡 for internal meetings where the user owes an input they haven't delivered.

- **[Meeting name — day/time]** — [why prep is needed] — [what's missing]

## 4. Draft messages for the top 3 most urgent

### To: [person], re: [topic]
> [Ready-to-paste message, concise, in the user's voice]

(repeat for 3 total)
```

**Ranking rules:**

- A commitment with an explicit deadline that has passed → 🔴.
- A commitment where someone is visibly waiting in Slack → 🔴.
- A commitment to an external stakeholder → 🔴.
- A commitment with a soft deadline ("next week", "soon") and no calendar event → 🟡.
- External kickoffs this week with no prep notes → 🔴 in Section 3.
- Internal recurring meetings where the user owes an input → 🟡 in Section 3.

### Draft messages — why these matter

Section 4 is the highest-leverage part of the report. The user can skim Sections 1–3 in 60 seconds, but Section 4 is where we save them the cognitive load of composing replies. Write messages that are:

- **Ready to paste.** Don't write "you could say something like…"; write the actual message.
- **In the user's voice.** If you've seen their Slack messages, match their tone (concise, lowercase-casual, first-name-only, etc.).
- **Action-forward.** Every draft should either close a loop or explicitly request what's needed to close it. Avoid filler ("just checking in…").
- **Respectful of context.** If the counterparty is senior/external, slightly more formal. Internal/peer = match their register.

### Save to disk

Save the final report to `forgot-check-YYYY-MM-DD.md` in the current working directory. Use today's date. If a file with that name already exists (user ran the skill twice in one day), append `-2`, `-3`, etc.

Tell the user the file path at the end of your reply so they can open it.

## Graceful degradation

Real tools fail. Handle these without blocking the whole report:

- **Granola times out** → fall back to `list_meetings` + `get_meetings`. If that also fails, tell the user what you couldn't pull and proceed with Calendar + Slack only.
- **Slack returns nothing for a broad search** → broaden the query (drop the `"I'll"` quoted phrases, just use `from:me after:DATE`). Empty results usually mean the search syntax was too narrow, not that the user has no open loops.
- **Calendar access fails** → note it in the report and skip the "underprepared meetings" section; still produce Sections 1, 2, and 4.

Always note in the report header what data you were able to pull and what you couldn't. The user needs to know whether the absence of a flag means "you're clear" or "I couldn't check."

## What to avoid

- **Don't pad the report to look thorough.** If Section 2 is empty, say "Nothing flagged" and move on. A three-line report is fine if the week was clean.
- **Don't list every meeting the user attended.** The report is about what's *missing*, not a meeting recap.
- **Don't invent deadlines.** If the source says "next week" and there's no firm date, say "no firm deadline" rather than making one up.
- **Don't surface things the user has clearly already handled.** If a commitment has a completed follow-up on the calendar or in Slack, it's done — skip it.

## Example invocation patterns

**"What am I forgetting this week?"** → default `days=14`, no focus, full sweep.

**"Quick check — last 3 days."** → `days=3`, no focus.

**"What's slipping on the Memphis deal?"** → `days=14`, `focus=Memphis`.

**"Am I ready for Monday?"** → default `days=14`, but emphasize Section 3 (underprepared meetings) in the output ordering.

## Final check before delivering

Before you print the report, sanity-check:

1. Did every 🔴 item get a draft message in Section 4? If not, either downgrade it or add a draft.
2. Does the report pass the "saved me 30 minutes" test? If the user would still need to dig through their tools to act on this, tighten it.
3. Are the Slack permalinks clickable? Every source citation should be a link the user can jump to.
