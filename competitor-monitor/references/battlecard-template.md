# Battlecard template

Full template for the output. Copy the structure. Adjust sections only if a dimension genuinely has no signal — don't fabricate content to fill a section.

---

```markdown
# Battlecard: <Competitor> — YYYY-MM-DD

_Scanned: <sources used — e.g., "web, Reddit (N posts across 3 subreddits), Capterra (N 1-2 star reviews), G2, LinkedIn, Wayback Machine"> | Focus: <focus or "general"> | Depth: <quick | standard | deep> | Lookback: last N days_

_Our product: <our product>._

---

## TL;DR

Three bullets maximum. What's changed that a rep needs to know *today*.

- <bullet 1>
- <bullet 2>
- <bullet 3>

---

## Recent moves

Dated bullets, most recent first. Each has: date, headline, source, implication.

- **YYYY-MM-DD** — <headline>. _Source: [Publisher](url)._ **Implication**: <one-line for our deals>.
- ...

If nothing in lookback window: "No material moves in the last N days. Last signal: <date> — <headline> ([source](url))."

---

## Pricing tear-down

Table:

| Tier | List price | Min units | Term | Onboarding | Active promos | Source |
|---|---|---|---|---|---|---|
| <tier> | $X/yr | N units | 1yr/2yr | $Y min | <promo + expiry> | [url](url) |
| ... | ... | ... | ... | ... | ... | ... |

**Historical pricing changes** (from Wayback Machine):
- <date> → <date>: <what changed — e.g., "base price raised from $2,500 to $3,000 (20%)">

**Discount levers observed in deals**:
- <lever 1> (e.g., "50% off onboarding if they sign by quarter-end")
- <lever 2>

---

## What users are complaining about

Themes, most recurrent first. Each: theme, recurrence count, verbatim quote with source and date.

### 1. <Theme> (seen N times)

> "<verbatim quote>" — [r/subreddit or review site](url), <reviewer role if known>, <date>

### 2. <Theme> (seen N times)

> "<quote>" — ...

---

## Recent feature launches / roadmap signals

### Launched (shipped within lookback window)

- **<Feature name>** — YYYY-MM-DD. <1-sentence description>. [source](url). **Our equivalent**: <our feature, or "gap">.

### In beta / announced / roadmap

- **<Feature name>** — <beta | announced | roadmap>. <description>. [source](url). **Our equivalent**: <ours or gap>.

---

## Executive & team changes

- **<Name>** — <role> — <joined | departed> <date>. <why it matters>. [source](url).

If no notable changes: "No notable leadership movement in the last N days."

---

## Hiring signal

- Open roles: **N** total, **M** posted in last 30 days
- Concentration areas: <e.g., "5 new SDR roles, 3 ML engineer roles, 2 VP/Head-of openings">
- Interpretation: <e.g., "Aggressive TOFU push + AI investment. Leadership gap at VP level.">
- Source: <competitor>/careers, LinkedIn Jobs — [url](url)

---

## Customer movement

### Recent wins (their marketing)
- **<Customer>** — <date if known>. [source](url). <Why they picked them, if stated>.

### Recent losses (our opportunities)
- **<Customer>** — switched to <replacement, if known> — <date>. [source](url). <Why, if known>.

These are gold. Weight heavily.

---

## Integrations & partnerships

### New integrations (last N days)
- <Integration> — <date> — [source](url). <Implication>.

### Ecosystem gaps (what they don't integrate with)
- <Tool X> — we integrate, they don't. Positioning lever.

---

## Security / legal / regulatory

Only include confirmed, sourced items. Skip this section entirely if nothing confirmed.

- **<Incident>** — YYYY-MM-DD. <description>. [source](url).

---

## Talking points for sales

### 1. If they say: "<anticipated prospect statement>"

**Say**: <exact words a rep should say on the call — spoken English, no jargon>

**Why**: <the source or fact backing it>

### 2. If they say: "..."

**Say**: ...

**Why**: ...

(3–5 total.)

---

## Objection handlers

### "<Objection>"

**Response**: <concrete, rep-usable answer>

**Evidence**: <fact or link>

### "<Objection>"

**Response**: ...

**Evidence**: ...

(2–4 total, covering the hardest ones.)

---

## Where we beat them

Concrete, sourced. No marketing language.

- <Feature/angle> — <one-line proof with source>.

---

## Where they beat us (be honest)

Concrete, sourced. Each item includes a pivot.

- <Feature/angle> — <one-line proof>. **Pivot**: <what to say / what to emphasize instead>.

---

## Switching-cost playbook

If the prospect is currently on <competitor>, here's the migration story:

- **Data export**: <what we know about their export capabilities>
- **Contract breakage**: <typical contract terms, auto-renewal dates>
- **Onboarding offer**: <our standard migration incentive>
- **Timeline**: <realistic migration timeline>
- **Risk areas**: <what usually breaks during migration from them>

---

## Qualification signals

Red flags that this is a low-probability deal against them:

- <Signal 1> (e.g., "Recently renewed 2-year contract — they're locked in")
- <Signal 2>

Green flags that suggest high probability:

- <Signal 1> (e.g., "Their VP CS just left")
- <Signal 2>

---

## Timing triggers

Events that make *now* the right time to displace:

- <Trigger 1> (e.g., "Their promo pricing expires June 30 — after that, renewal shock")
- <Trigger 2>

---

## Sources

All citations, ordered by recency. Each: title, URL, date accessed.

- [Title](url) — YYYY-MM-DD
- ...

---

## Delta since last battlecard

(Only if `compare_to` parameter was provided.)

### New since last battlecard
- <item>

### Changed since last battlecard
- <item>

### No longer relevant (previously flagged, now stale)
- <item>
```

---

## Template usage notes

- Sections with **no signal** should say so explicitly, not be omitted. Blank sections hide holes; labeled-as-empty sections tell the rep where they still need to dig.
- **Order matters**. Reps scan top-down. TL;DR → recent moves → pricing → complaints are the most-read sections. Don't bury the lede.
- **Talking points are the core.** If everything else is thin but talking points are strong, the battlecard is still useful. If talking points are weak, the battlecard is useless no matter how rich the rest is.
- **Quotes must be verbatim.** Don't paraphrase user complaints. Reps use exact quotes to establish credibility. Paraphrase kills that.
- **Dates on everything.** No undated claims.
