---
name: daily-ops-briefing
description: >
  Generates a weekly ops briefing by scanning specific Slack channels for announcements,
  updates, and to-dos directed at district-onboarding-managers, district-partnerships-managers,
  and technical-implementation. Categorizes findings into Ops Updates, Process Changes,
  Learnings, Resources/FYIs, Pre-work, and Product Launches, then posts a formatted summary
  to the user's private Slack for review. Use this skill whenever the user asks for a "weekly
  ops briefing", "district team summary", "weekly update for district managers", "ops digest",
  "run the weekly briefing", or any request to compile or summarize Slack updates for the
  district or technical implementation teams. Also trigger when the user says things like
  "what happened this week in districts?" or "compile updates for the team".
---

# Daily Ops Briefing

You are generating a weekly ops briefing for the district and technical implementation teams.
Your job is to scan the right Slack channels, pull out only what matters to these teams, sort
it into the right buckets, and produce a clean summary the user can review before sharing.

## Parse parameters

Check the user's message for:
- `week=YYYY-MM-DD` — the Monday of the week to summarize (default: most recent Monday)
- `days=N` — alternatively, how many days back to scan (default: **7**)
- `post=true/false` — whether to actually post the message to Slack after drafting, or just show it (default: **false** — always show for review first, only post if explicitly asked)

Calculate date range: from start of the target week through today (or Friday if the week is complete).

## Step 1 — Search target channels

Search each of these channels for messages from the date range:
- `#districts`
- `#districts-ops`
- `#districts-private`
- `#cs-whole-team`
- `#sales-success`
- `#gluten-free-dpms`
- `#district-kickoffs`
- `#district-product`
- `#product-launches`

Use `slack_read_channel` for each channel (with the date range as context) and/or
`slack_search_public_and_private` to find messages that:
1. Are **in** those channels, AND
2. **@mention** any of:
   - `@district-onboarding-managers`
   - `@district-partnerships-managers`
   - `@technical-implementation`

Run the channel reads in parallel where possible — there are nine channels, so batch them.

For threads that look relevant, use `slack_read_thread` to get the full thread context
(the original message might just say "see thread" but the substance is in replies).

> **Why the @mention filter matters**: These three groups receive a high volume of general
> Slack traffic. Messages that explicitly @mention one of the groups are ones where the
> poster intended to reach that audience — those are the high-signal ones worth surfacing.
> Don't include every message in the channel, only those directed at the groups.

## Step 2 — Categorize messages

For each relevant message, assign it to exactly one category. When in doubt, pick the most
specific category that fits (e.g., something that is both a process change and a learning
should go under Process Changes since that's more actionable).

### Category definitions

**Ops Updates**
Operational changes to tools or systems, especially SFDC (Salesforce) and Asana. Examples:
new fields added, workflow automations changed, pipeline stages renamed, Asana project
structure updated, reporting changes.

**Process Changes**
Changes in *who* does what or *when* things happen — workflow ownership, handoff sequences,
new steps in an existing process, responsibilities shifted between roles or teams. Not about
tools, about the human choreography.

**Learnings**
Aha moments, lessons from the field, things that worked or didn't, patterns noticed across
accounts, insights from launches or implementations. Anything shared as "we learned that..."
or "heads up — this is what we found...".

**Resources or FYIs**
New docs, templates, Notion pages, guides, recordings, or reference material shared for
the team's awareness. Also announcements that don't require action but are good to know.

**Pre-work**
Upcoming required reading, preparation, training, or assignments *before* a specific event
(call, launch, meeting). Characterized by future timing and expectation of completion.

**Product Launches**
New product features, tool rollouts, release announcements, sunset notices, changes to
existing product behavior. Includes both launches and notable edits to live products.

### Handling uncategorizable messages

If a message genuinely doesn't fit any category (e.g., it's just social/celebratory), skip
it — don't force it in. Quality over completeness.

## Step 3 — Format the briefing

Use this exact template:

```
📋 *Weekly Ops Briefing* — Week of [Mon Date] – [Fri Date]
_For: @district-onboarding-managers | @district-partnerships-managers | @technical-implementation_
_Sources: #districts #districts-ops #districts-private #cs-whole-team #sales-success #gluten-free-dpms #district-kickoffs #district-product #product-launches_

---

*⚙️ Ops Updates*
_(Updates to SFDC, Asana, or operational tooling)_

• [Summary of update] — [link or channel reference if available]
• ...

---

*🔄 Process Changes*
_(Changes in who does what or when)_

• [Summary] — [source]
• ...

---

*💡 Learnings*
_(Aha's, field insights, lessons from the team)_

• [Summary] — [source]
• ...

---

*📎 Resources & FYIs*
_(New docs, templates, need-to-know info)_

• [Summary] — [link if available]
• ...

---

*📚 Pre-work*
_(Upcoming required reading or prep)_

• [Summary — include deadline or event it's tied to] — [source]
• ...

---

*🚀 Product Launches*
_(New features, releases, product changes)_

• [Summary] — [source]
• ...

---
_Generated [today's date] | [N] items across [N] channels_
```

**Formatting rules:**
- Each bullet should be 1–2 sentences max — scannable, not exhaustive
- If a thread has more detail, add `(see thread in #channel-name)` at the end of the bullet
- If a section has nothing to report, write `_Nothing this week_` rather than omitting it
- Keep the whole briefing tight — this is a digest, not a transcript
- Use Slack markdown (asterisks for bold, underscores for italics, backticks for code)

## Step 4 — Post or draft

**By default, show the briefing in the conversation and ask if they'd like it posted.**

If `post=true` was specified, or the user says "go ahead and post it" or similar:
- Use `slack_send_message` to send to the user's own DM (message yourself) for review
- OR if the user specified a channel (e.g., "post to #my-channel"), post there instead

If posting, confirm the destination before sending.

**Never auto-post to any team channel** without explicit instruction — this briefing is
meant to be reviewed first.

## Edge cases

**Channel not found or no access**: Note it in the footer ("⚠️ Could not read: #channel-name")
and continue with the rest.

**No @mentions of target groups this week**: Report honestly — "No messages directed at
these groups were found this week" — and offer to do a broader scan (without the @mention
filter) if the user wants.

**Duplicate coverage**: If the same announcement appeared in multiple channels, list it once
and note `(mentioned in #channel-a, #channel-b)`.

**Very long threads**: Summarize the resolution/outcome, not the full discussion.
