---
name: slack-debrief
description: Scan the user's Slack channels, find the highest-signal conversations (threads with the most replies, unresolved debates, decision posts), and produce a concise Slack-formatted summary of each — what it was about, who weighed in, and what was decided. Use whenever the user asks for a "Slack debrief", "catch me up on Slack", "what did I miss in Slack", "what are people arguing about", "summarize the big threads this week", or any variation of digesting Slack activity across channels. Also trigger when the user has been heads-down or out and wants the shape of recent discussion without reading every channel. Output is written both as a file (~/Desktop/Claude Class/slack-debrief-YYYY-MM-DD.md) and as text the user can copy-paste directly into a Slack message to share with their team.
---

# slack-debrief

Produces a short, punchy summary of the most-discussed Slack threads from the user's recent activity — formatted as a Slack message they can read in the terminal or paste into a channel as a weekly digest.

## When the user wants this

Monday mornings, return-from-PTO, or any moment they feel they've lost the thread of what the team is discussing. They want **signal, not a transcript** — the 5-10 conversations that actually mattered, summarized tightly.

## Parameters

Parse from the user's invocation:

- **`days`** — time window (default `7`). Honor "yesterday" → 1, "last week" → 7, "this month" → 30.
- **`channels`** — comma-separated channel names to include (default: all channels the user is a member of, excluding DMs and noisy bot/alert channels). Accept bare names like `district-leads` or prefixed `#district-leads`.
- **`exclude`** — channels to skip beyond the noisy defaults.
- **`top`** — how many threads to include (default `10`).

## Why this is tricky (read before building the run)

Slack's web client uses heavy virtualization: message elements only exist in the DOM when scrolled into view. Naive `innerText` grabs on the main pane will return empty. The extraction strategy that actually works — learned from the `what-did-i-forget` skill run:

1. Navigate to a specific channel URL (`https://app.slack.com/client/<WORKSPACE>/<CHANNEL_ID>`) and wait ~2s.
2. Scroll the message scroller (`.c-virtual_list__scroll_container`) to the top to force older messages to render, then back down.
3. Query messages with `document.querySelectorAll('[data-qa="message_container"]')` — this reliably returns message DOM nodes with `innerText`.
4. Thread reply counts live on the parent message in `[data-qa="reply_bar_count"]` or in text like "23 replies". Capture these.

Don't try to use the "Activity" or "Highlights" pages — they render async and leave list items empty. Channel-by-channel is the working path.

If the Chrome extension is not reachable, stop and tell the user: *"Chrome extension isn't connected — I can't read Slack. Open Chrome with the Claude extension signed in, then re-run me."* Same fail-fast rule as `what-did-i-forget`.

## Workflow

### Step 1 — Identify the workspace and target channels

Read `~/Library/Application Support/Slack/storage/root-state.json` to get the primary workspace ID:

```bash
python3 -c "import json; d=json.load(open('$HOME/Library/Application Support/Slack/storage/root-state.json')); [print(w['id'], w['domain'], w.get('name','')) for w in d.get('workspaces',{}).values()]"
```

Default to the user's primary workspace (usually the one with the most recent activity — if unclear, ask). Once you have the workspace ID, navigate to the Slack home page in Chrome and enumerate channels via the sidebar tree (`[role="treeitem"]`). Exclude by default anything matching:

- DM categories (names that are just a person's name or comma-list of names)
- Channel names containing `alerts-`, `-bot`, `-alerts`, `salesforce-bot`, or similar noise markers
- Anything in the user's `--exclude` list

If the user passed `--channels`, use that list directly (look up each channel's ID by clicking through the sidebar, or use the quick-switcher at `Cmd+K`).

### Step 2 — For each channel, pull recent messages + thread reply counts

For each target channel:

1. Navigate to `https://app.slack.com/client/<WORKSPACE>/<CHANNEL_ID>`
2. Wait ~2 seconds for initial render
3. Run the scroll-and-extract JavaScript (see `scripts/extract_channel.js`), which:
   - Scrolls the virtual list to force message rendering
   - Captures each parent message's text, author, timestamp, and thread reply count
   - Returns JSON with messages sorted by reply count descending

Keep only messages within the `--days` window. Capture the top 3–5 most-replied threads per channel as candidates.

### Step 3 — For the top candidate threads, open the thread panel and read replies

Merely reading the reply count isn't enough — we need the actual discussion to summarize. For each candidate thread:

1. Click the reply count link on the parent message (or use the URL pattern `?thread_ts=<timestamp>` if you can find the ts).
2. Wait for the thread sidebar to render.
3. Extract replies with `document.querySelectorAll('[data-qa="message_container"]')` inside the thread pane.
4. Capture reply text, author, and timestamp.

If extracting replies is fragile (Slack sometimes collapses), fall back to just the parent message + reply count; note this as "summary based on opening post only" in the output.

### Step 4 — Rank and summarize

Across all channels, rank the gathered threads by a composite signal:
- **Primary:** reply count (more replies = more engagement)
- **Tiebreaker:** presence of decision-y language in the thread ("let's go with", "decided", "approved", "agreed", "pushing back", "blocker"), plus reactions if visible
- **Penalty:** threads that are pure kudos/celebration (emoji-only replies, "🎉🎉🎉" chains) are usually not "important" — deprioritize them unless the user specifically asks for wins.

Take the top `--top` (default 10). For each, write a tight summary:

- **What it's about** (1 sentence)
- **Who weighed in** (names, comma-separated — max 5, then "+N others")
- **What was decided / current status** (1-2 sentences — be precise about whether a decision was made, is pending, or the thread fizzled)
- **Channel + thread link** (the Slack deep link)

### Step 5 — Write the output in Slack mrkdwn

Slack's markdown is a *subset* of standard markdown. The rules that matter:

- `*bold*` uses single asterisks (not double)
- `_italic_` uses underscores
- `~strikethrough~` uses tildes
- `> blockquote` for quoting
- Bulleted lists use `•` (the Unicode bullet) or `- ` — Slack converts `- ` automatically but `•` is safer
- Code spans use single backticks, code blocks use triple backticks
- Line breaks are literal `\n` — no double-newline paragraphs needed
- Links: `<https://example.com|link text>` (angle brackets, pipe separator)
- User mentions use `<@U123ABC>` — you usually won't have IDs, so fall back to plain names like `Jeff` or `@Jeff`

Save to `~/Desktop/Claude Class/slack-debrief-YYYY-MM-DD.md` AND print the same content to the terminal so the user can copy-paste without opening the file. Use this structure:

```
*Slack Debrief — <Mon DD>*
_Last <N> days · <M> channels · top <K> threads_

*1. <Short thread title — 6-10 words>*  ·  #channel-name
<1-sentence topic summary>.
_Who:_ Name1, Name2, Name3 +2 others
_Status:_ <Decision made / Pending / Fizzled / Blocked on X>
<https://app.slack.com/...|Open thread>

*2. <Next thread>*  ·  #other-channel
...

*Footer*
_Skipped: <N> channels (<excluded list>)._
_Gaps: <anything you couldn't access>._
```

Keep each thread block to 3-4 lines. The whole debrief should fit in a single Slack message (roughly under 3000 chars) — if it won't, trim the less urgent items rather than truncating mid-thread.

### Step 6 — Tell the user what you produced

After writing, give a one-line summary: *"Debriefed 24 threads across 11 channels. Top item: the GTM forecast disagreement in #district-leads-funnel-health (31 replies, still unresolved). Full output at ~/Desktop/Claude Class/slack-debrief-2026-04-23.md and printed above."*

## Style notes for the summaries

- **Be specific.** "Discussion about Q2 planning" is useless. "Debate about whether to cut the India GTM pilot or double down — Ali pushing for cut, Jeff pushing to extend 1 quarter" is useful.
- **Say what was decided, not what was said.** If the thread ended without resolution, say "still open" — don't manufacture a conclusion.
- **Name names.** Who drove the discussion, who pushed back, who made the call.
- **No emoji except what's functional.** Skip the rocket ships and fires. If reactions are significant (e.g., a 👀 from the CEO on a proposal), mention them plainly: "Jeff reacted 👀 but hasn't weighed in yet."
- **Dont invent details.** If you can only see the parent message, summarize that and note you couldn't read the replies. Fabricating a "decision" the user then refers to would be much worse than an honest "couldn't read."

## Bundled resources

- `scripts/extract_channel.js` — the JavaScript snippet to run via `mcp__Claude_in_Chrome__javascript_tool` to extract messages + reply counts from a channel view. Call this rather than re-writing the scroll-and-query logic each time.
