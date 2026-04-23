---
name: gong-community-handoff
description: Mines Gong call transcripts from district leader conversations to surface moments where a mentor, advocate story, or teacher proof point could close a trust or adoption gap — then hands off to community marketing. Use this skill whenever the user mentions a Gong call, district call review, call transcript, or handoff to community. Also trigger when the user says things like "I just got off a call with a district," "can you review this transcript," "who should I loop in from community," or "what's the community play here." The skill does not find new advocates — it finds opportunities to deploy the ones we already have.
---

# gong-community-handoff

## Core premise
District leaders frequently doubt whether teachers in their district will actually adopt a tool or succeed with a specific use case. Teachers in those same districts (or comparable ones) are often already using ClassDojo successfully — but that proof never reaches the conversation. This skill bridges that gap by scanning call transcripts for the exact moments where a peer voice would land better than a vendor answer.

## Before you begin
Read `references/reference.md` now. It contains:
- Definitions of active community programs (Mentor Program, Bettermode, More for Mentors, customer stories, reference asks)
- Mentor profile dimensions to use when describing ideal matches
- Compliance rules (no public reference without legal sign-off, District A/B/C naming)
- A gold example showing input → output for a real call

## When NOT to run this skill
Stop and flag instead:
- Transcript is a support escalation or churn conversation → flag as **CS handoff**
- Account is flagged at-risk in CRM → flag as **CS handoff** and stop
- Call is with a teacher, not a district leader or administrator → out of scope

## Parameters
The user may supply these inline or you can ask for them:

| Parameter | Required | What to do if missing |
|---|---|---|
| `transcripts_or_summaries` | Yes | Ask the user to paste or pull from Gong |
| `goal` | Yes | Ask: deploy-advocates / find-story-gaps / all |
| `account_context` | No | Infer from transcript if possible |
| `constraints` | No | Assume none unless stated |
| `include_drafts` | No | Default false |

## Do not infer rule
Never invent mentor profiles, stories, or programs not supported by the transcript or `references/reference.md`. If the transcript is thin, mark affected items `needs verification`. Never make product or feature promises.

## Signal rubric
Scan every transcript for these four gap types. Extract verbatim short quotes with speaker label when available. Do not paraphrase — the quote is the evidence.

### 1. Adoption uncertainty
The district leader doubts whether teachers would actually use the tool or stick with it.
> "I'm not sure my teachers would buy in" / "We've tried tools before and they don't get used" / "How do you get teachers to actually adopt this?"

### 2. Use case doubt
The leader is unsure the tool works for their specific context — grade level, subject, district size, demographic, language.
> "Does this work for middle school?" / "We're a bilingual district, I'm not sure this fits" / "Our teachers are not very tech-savvy"

### 3. Social proof gap
The leader wants to hear from peers, not vendors.
> "Has anyone in a district like ours used this?" / "Do you have any references?" / "I'd love to talk to another principal"

### 4. Objection pattern
Recurring hesitation that suggests a missing story or content asset — something a mentor voice or case study could neutralize better than a sales response.
> "We already use [competitor]" / "The teachers union would push back" / "Budget is tight and I need to justify this"

## Confidence anchoring
- **High** — direct quote, explicit hesitation or ask
- **Medium** — behavioral signal, no direct quote
- **Low** — inferred from context or thin transcript

## Output format
Produce all three sections below. Do not narrate your process — go straight to the output.

### Executive line
2–3 sentences. What is the single most important deployment opportunity — the one doubt that a well-matched mentor or story could most directly neutralize?

### Deployment opportunities
Ranked table. For each row:

| Gap / doubt (quote) | Gap type | Ideal mentor or story profile | Why this would land | Suggested ask to AJ | Confidence |

- **Gap / doubt**: verbatim quote if available, otherwise Gong summary language in italics
- **Ideal mentor or story profile**: describe the *type* — do not invent a name. Use the profile dimensions from `references/reference.md` (grade level, district size, region, use case, language context, etc.)
- **Suggested ask to AJ**: one sentence — what AJ should go do next

### Watchouts
Doubts or objections that sound like community plays but are actually CS, product, or pricing issues. Label each clearly:
- **CS handoff**
- **Product feedback**
- **Pricing conversation**

### Draft Slack message to self
Only include if the user set `include_drafts: true`. Short self-note. Include: district name (use "District A" if PII concern), top gap, ideal asset profile to find, who to loop in (CSM, AE). No fluff.
