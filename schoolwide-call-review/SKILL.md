---
name: schoolwide-call-review
description: >
  Use this skill any time the user asks to review, analyze, or summarize their
  team's recent Gong calls for conversations about "going schoolwide" with
  ClassDojo — including phrasings like "pull my team's schoolwide calls",
  "review schoolwide conversations from the last 2 weeks", "what objections
  are we hearing on schoolwide", "how are we pitching schoolwide", "Gong
  schoolwide review", or "compare our schoolwide pitch to the enablement".
  Also trigger when the user asks how reps are handling schoolwide objections,
  whether the team is on-message versus the schoolwide playbook, or for a
  sales readout on schoolwide conversations. The skill pulls recent calls from
  the Gong API, filters for schoolwide discussion, synthesizes what leaders
  are saying and what objections are coming up, compares rep pitches to the
  bundled ClassDojo schoolwide enablement, and writes a coach-ready readout
  to schoolwide-call-review.md. Always prefer this skill over ad-hoc
  summarization when the topic is ClassDojo schoolwide sales conversations.
---

# Schoolwide Call Review

Turn the last N days of the user's team's Gong calls into a coaching-ready
readout about how the team is selling "going schoolwide" with ClassDojo.

## What this skill does

1. **Fetches** calls + transcripts from the Gong API for the user's team
2. **Filters** to calls with substantive schoolwide discussion
3. **Synthesizes** what school leaders are saying and what objections came up
4. **Compares** the team's pitches against the bundled ClassDojo enablement
5. **Writes** a structured readout to `schoolwide-call-review.md`

---

## Prerequisites

The skill uses the Gong REST API with credentials at `~/.gong/credentials`:

```
GONG_ACCESS_KEY=...
GONG_ACCESS_KEY_SECRET=...
```

If the file is missing or empty, stop and tell the user to generate API
credentials in Gong (Company Settings → Ecosystem → API) and drop them in
that file with `chmod 600`. Do not ask the user to paste credentials into
chat.

---

## Parameters

Gather these before running. If any are missing and the user hasn't specified,
use reasonable defaults and tell the user what you assumed.

| Param | Default | Notes |
|---|---|---|
| `days` | 14 | How many days back to pull |
| `owner_email` | `dave.herron@classdojo.com` | The user whose team this is. Confirm once on first run; remember for subsequent runs. |
| `team` | `schoolwide-reps` | Default `schoolwide-reps` covers the 5 reps running schoolwide conversations: **Shanieka Myles, Natasha Fisher, Sarah Zients, Nicole Kindos, Brianna Casas**. Other shorthands: `direct-reports` (all 12 active reports), `me`. Also accepts a comma-separated email list. The `schoolwide-reps` list lives in `scripts/gong_fetch.py` under `TEAM_SHORTHANDS` — edit there to add/remove reps. Don't ask about this parameter unless the user explicitly scopes differently (a specific rep, "everyone", etc.). |
| `extra_enablement` | none | Optional. File paths or pasted text of updated enablement to add to the comparison. The bundled playbook at `references/schoolwide-playbook.md` is always used. |

---

## Step 1 — Fetch calls with `scripts/gong_fetch.py`

Run the fetcher. It writes raw Gong JSON to a work directory you can then
read piece by piece.

```bash
WORK=/tmp/schoolwide-$(date +%Y%m%d-%H%M%S)
python3 <SKILL_DIR>/scripts/gong_fetch.py \
    --owner-email <owner_email> \
    --team <team_spec> \
    --days <N> \
    --out "$WORK"
```

What the script produces:

- `$WORK/summary.json` — window, team roster, total call count
- `$WORK/calls.json` — one entry per call, with metaData + parties + content (brief, outline, keyPoints, highlights, topics, trackers)
- `$WORK/transcripts/<callId>.json` — full transcript per call

If there are **>60 calls in the window**, pass `--skip-transcripts` on the
first run, triage candidates from metadata (Step 2a), then re-run with
`--transcript-call-ids <ids>` to pull only the candidate transcripts. This
saves a lot of API load and token cost.

---

## Step 2 — Filter to schoolwide calls

### 2a. Metadata triage (cheap)

Load `calls.json`. For each call, concatenate the title + `content.brief` +
`content.outline` + `content.keyPoints` + `content.highlights` into a single
text blob. Match against these patterns (case-insensitive):

- `\bschoolwide\b`, `\bschool[- ]wide\b`
- `whole school`, `every classroom`, `every teacher`, `all staff .* classdojo`
- `going schoolwide`, `go schoolwide`, `full rollout`, `partial adoption`
- `uneven adoption`, `half our teachers`, `half the staff`
- Adoption-breadth phrasing in the context of a school or district

This is intentionally loose — better to over-include at this stage and
tighten on transcript content next.

### 2b. Transcript qualification (accurate)

For each triaged candidate, load `transcripts/<callId>.json` and read the
actual conversation. A call **qualifies** if there is at least one
substantive exchange (2+ minutes or a clear decision point) about moving
the school toward whole-school / schoolwide adoption of ClassDojo.

A call **does not qualify** if "schoolwide" appears only in passing
(a title reference, a logistical mention, or a single unanswered keyword).

Keep an exclusion log with one-line reasons — the user will want to
spot-check.

### Note on team composition

The user's team composition matters for interpretation. Account Executives
selling new-logo districts will have different call profiles than
Implementation Specialists helping existing schools expand adoption. Look at
titles in `summary.json`'s team roster and frame the analysis accordingly —
"the team is deploying the schoolwide expansion play at already-partner
schools" reads differently from "the team is selling schoolwide to new
districts." Say which lens you're using up front.

---

## Step 3 — Read the playbook, then synthesize

Read `references/schoolwide-playbook.md` before any synthesis. It contains:

- The five value pillars
- Expected objections and the enablement-recommended handling
- Proof-point stats reps should reach for
- The three canonical sales situations
- The role-play scenarios reps train against

For each qualifying call, extract:

1. **Context** — who's in the room, stage of the relationship, the "why now"
2. **What the customer said** — their stated reasons for going schoolwide, objections/concerns they raised (verbatim quotes when possible)
3. **What the rep said** — which of the 5 pillars they named, which proof-point stats they cited, how they handled objections
4. **Outcome** — what did the rep commit to next

Then roll up across calls:

- **Conversation patterns** (3–5 clusters; be concrete, not generic)
- **Top reasons leaders want schoolwide** (rank-ordered, with verbatim quotes)
- **Top objections** (rank-ordered, with rep response quality vs. enablement)
- **Team strengths** (tied to specific calls and moments)
- **Coaching opportunities** (tied to specific calls, with the
  enablement-aligned move the rep missed)

### Rigor rules

- Ground every claim in a specific call ID, rep, and moment. If you can't
  cite, cut the claim or mark it "impressionistic".
- Do not invent quotes or upgrade imprecise language ("lots of engagement"
  is not "2x engagement" unless the rep actually used that framing).
- Do not inflate the scorecard — credit a pillar or stat only when the rep
  actually named it, not when they gestured toward it.
- A pattern seen in 2 calls is a hypothesis. A pattern in 5+ is a trend.
  Label accordingly.

---

## Step 4 — Compare to the enablement

Score each qualifying call against the seven enablement expectations from
`references/schoolwide-playbook.md`:

1. Discovery questions asked before pitching
2. Named ≥3 of the 5 value pillars
3. Cited at least one proof-point stat
4. Referenced a proof-point account (Hamilton Elementary or similar)
5. Reframed objections using the enablement answers
6. Framed schoolwide as amplifying existing teacher adoption (not replacing)
7. Tied schoolwide to a specific leader priority (renewal, board, equity, visibility)

Produce a scorecard table in the readout (see
`references/readout-format.md` for the exact structure).

If the user supplied `extra_enablement`, read it too and add any new
expectations to the scorecard.

---

## Step 5 — Write the readout

Output to `schoolwide-call-review.md` in the current working directory,
following the exact structure in `references/readout-format.md`. The sections are:

1. What kinds of schoolwide conversations are happening?
2. Why school leaders are choosing to go schoolwide
3. Objections and concerns we heard
4. What the sales team is doing well
5. Where the team can improve
6. Enablement alignment scorecard
7. Recommended next actions
8. Appendix: call-by-call notes

Consistency matters — this readout is meant to run on a cadence, and the
user compares weeks over time.

Include Gong call URLs (from `metaData.url`) in the appendix so the user
can jump straight to a call from the readout.

---

## Step 6 — Short chat summary

After writing the file, give the user a 4–6-line chat summary:

- Window, calls scanned, calls that qualified
- One sentence on the team lens (AE vs IS, etc.)
- 1–2 biggest strengths
- 1–2 biggest coaching opportunities
- Where the file was written

Do **not** dump the full readout into chat — the file is the deliverable.

---

## Common pitfalls to avoid

- **Don't skip Step 2b.** Title + brief triage over-selects. Transcript-level
  qualification is what produces a trustworthy readout.

- **Don't ask for credentials in chat.** The skill uses the file at
  `~/.gong/credentials`. If it's missing, point the user at the file, don't
  take values inline.

- **Don't pull transcripts you don't need.** For windows with >60 calls, use
  the two-phase fetch (triage first, transcripts second) — it's both faster
  and cheaper.

- **Don't use relative dates in the final readout.** "On 2026-04-15", never
  "last Tuesday" — the file will be read weeks later.

- **Don't overreach on small N.** If the window surfaces 3 qualifying calls,
  the readout should be based on 3 calls and say so plainly. Don't pad with
  impressionistic takes to make it look more substantial.
