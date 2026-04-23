---
name: competitor-monitor
description: Comprehensive competitive intelligence scan — searches the open web, Reddit, review sites, LinkedIn, job boards, press wires, the Wayback Machine, app stores, and the competitor's own properties to produce a sales battlecard with talking points, objection handlers, pricing tear-downs, exec-change tracking, customer win/loss signals, and switching-cost playbooks. Use this skill whenever the user asks about a competitor by name (ParentSquare, Apptegy, Thrillshare, PowerSchool, Seesaw, Remind, etc.), asks for a battlecard, asks what a competitor has been doing, asks how to position against someone, asks for fresh competitive intel, wants to prep a rep for a deal involving a competitor, wants win/loss analysis against a specific competitor, or asks about a competitor's pricing, launches, team changes, or customer churn. Also trigger for phrasings like "what's the latest on X", "update me on X", "give me ammo for the X deal", "how do we beat X", "what are people saying about X", "is X hiring / firing / growing / shrinking", "who just switched away from X", or "who just bought X". Prefer this skill over generic web search whenever the intent is competitive — the structured battlecard output is more useful than raw results.
---

# Competitor Monitor

Comprehensive sales battlecard builder. Pulls from the open web, Reddit, review sites, LinkedIn, job boards, press wires, the Wayback Machine, app stores, YouTube, and the competitor's own properties. Produces an output a rep can use on a live deal and a PMM can use for messaging decisions.

**Research philosophy**: prefer direct browser navigation (via Claude-in-Chrome) and structured API/JSON endpoints over generic WebSearch. WebSearch is a URL discovery tool; the real signal is in the page content, and reviews + Reddit + exec changes are systematically under-indexed by search engines. Going direct is 10x more reliable.

## When to run

Invoke whenever the user:
- Names a competitor and asks for an update, battlecard, talking points, or positioning
- Says they have a deal against a specific competitor
- Wants to know what users are saying about a competitor
- Asks "what's new with X", "how do we beat X", "give me the latest on X"
- Asks about a competitor's pricing, funding, layoffs, new hires, or customer wins
- Asks for prep material before a competitive webinar, demo, or RFP response

Proceed with defaults if parameters aren't specified.

## Parameters

- `competitor` — **required.** Company name (e.g., "ParentSquare", "Apptegy", "Seesaw"). Can be an array for multi-competitor battlecards.
- `days` — lookback window for "recent" (default **30**). Accept "this week" (7), "last month" (30), "this quarter" (90), "this year" (365).
- `focus` — optional angle. Examples: `"pricing"`, `"district customers"`, `"complaints"`, `"product launches"`, `"attendance feature"`, `"AI strategy"`, `"churn"`, `"team changes"`. Biases ranking.
- `our_product` — optional. What we're selling (default: infer from context). Used to frame talking points as "us vs. them".
- `depth` — `"quick"` (30 min, moves + top complaints + 3 talking points), `"standard"` (default — everything in the template), `"deep"` (adds Wayback diff, exec LinkedIn trawl, mobile app review sweep, win/loss customer interviews via case studies).
- `compare_to` — optional. Path to a previous battlecard for the same competitor. When provided, produce a **delta battlecard** highlighting what changed since the last version.

## Required tools

Tiered — use the best available. None of the lower tiers are fallbacks for lack-of-access; they're supplements to be used in parallel.

### Tier 1: Direct browser — Claude in Chrome connector

- `mcp__Claude_in_Chrome__tabs_context_mcp` — ensure tab exists
- `mcp__Claude_in_Chrome__navigate` — go to Reddit, LinkedIn, review sites, competitor pages
- `mcp__Claude_in_Chrome__get_page_text` — article extraction
- `mcp__Claude_in_Chrome__javascript_tool` — targeted DOM queries (reviews, pricing tables, LinkedIn sidebars)
- `mcp__Claude_in_Chrome__find` — locate specific elements by description
- `mcp__Claude_in_Chrome__read_page` — accessibility tree when JS extraction is overkill
- `mcp__Claude_in_Chrome__read_network_requests` — discover the competitor's own internal API endpoints (useful for pricing calculators, product catalogs)
- `mcp__Claude_in_Chrome__computer` — click through multi-page review lists, paginated search results

### Tier 2: Static fetch

- `WebFetch` — direct URL fetch + prompt extraction; ideal for a known URL
- Reddit JSON endpoints (see below) via WebFetch — no auth, clean structured data **(often blocked in hosted environments — see Apify path below)**
- Wayback Machine via `http://web.archive.org/web/*/<url>` — historical pricing + feature pages

### Tier 2a (preferred for Reddit): Apify scrapers

Reddit is frequently blocked by browser and WebFetch safety policies. When this happens, use one of two bundled Apify actors via the helper scripts:

**Default — `trudax/reddit-scraper-lite`**:
```bash
scripts/reddit_via_apify.sh <competitor> [time_range] [max_items]
# e.g.
scripts/reddit_via_apify.sh "ParentSquare" month 50
```
Cheap, fast, sufficient for most battlecards.

**Deep mode — `trudax/reddit-scraper` (full, actor ID `FgJtjDwJCLhRH9saM`)**:
```bash
scripts/reddit_via_apify_deep.sh <competitor> [time_range] [max_items] [community]
# examples
scripts/reddit_via_apify_deep.sh "ParentSquare" year 50 k12sysadmin
SEARCH_COMMENTS=true scripts/reddit_via_apify_deep.sh "ParentSquare" month 100
```
Use when you need comment-body search, subreddit-scoped search, date cutoffs, or large-volume pulls. Costs more CUs — default to lite, escalate to deep only when lite returns thin or `depth: "deep"` is passed.

Both scripts read the Apify token from `$APIFY_TOKEN` (env var) or `~/.apify_token` (chmod 600 file), in that order. **Never hardcode the token in skill files or battlecards.** See `references/reddit-playbook.md` for setup, input schemas, parsing guidance, and token security.

Output (both actors): JSON array of posts with title, communityName, author, body, comments, upVotes, numberOfComments, createdAt.

### Tier 3: Discovery

- `WebSearch` — URL discovery. **Do not rely on WebSearch snippets for final claims** — they paraphrase and lose specificity. Use it to find URLs, then fetch.

### Optional connectors (use if available)

- **Slack connector** — search your own company's Slack for internal mentions of the competitor (AEs often share war stories that never make it to Gong)
- **Gong connector** — if competitor is mentioned by buyers on calls, quotes are gold
- **Notion / Google Drive** — existing internal docs about the competitor
- **mcp-registry `search_mcp_registry`** — check if a dedicated connector for Crunchbase, LinkedIn, Apollo, etc. has been published

## Research dimensions

A comprehensive scan covers **twelve dimensions**. For each, I list the primary source, the research technique, and what "good signal" looks like. See `references/research-sources.md` for the full source catalog with URL patterns.

### 1. Recent moves (press & news)

**Sources**: Google News, PR Newswire, BusinessWire, industry trade pubs (EdSurge, THE Journal, Education Week for K-12; relevant trade pubs for other verticals), the competitor's own `/press` or `/news` page.

**Technique**: WebSearch with date-scoping (`<competitor> news <year>`), then Chrome-navigate to top 3–5 results and `get_page_text`. Also navigate directly to `<competitor>.com/press`.

**Good signal**: dated press releases about funding, M&A, leadership changes, major customer wins, major customer losses, strategic partnerships.

**Noise to ignore**: content-mill summaries that repackage the press release without new info; sponsored content; awards from vendor-paid programs.

### 2. Pricing

**Sources**: competitor's own pricing page; G2/Capterra/GetApp pricing sections (they sometimes list numbers the vendor hides); AWS Marketplace / Azure Marketplace listings; state procurement portals (for gov/edu, Sourcewell, TIPS, state contracts); Wayback Machine for pricing history.

**Technique**:
1. Chrome-navigate to `<competitor>.com/pricing`, extract text and any pricing tables
2. Check Wayback Machine for the same URL 6 and 12 months ago — surfaces price increases
3. Search for the competitor on state procurement sites (their pricing is often published as part of approved-vendor contracts)

**Good signal**: tier minimums, onboarding fees, promo expirations, multi-year discounts, per-seat vs. per-student vs. flat rates, add-on pricing. Numbers with dates.

**Output format**: a **pricing tear-down** table — rep can pull it up on a call.

### 3. User complaints (Reddit + reviews)

**Reddit is the highest-signal source here and requires the most care.** See `references/reddit-playbook.md` for the full methodology. Access path in priority order:

1. **Apify `trudax/reddit-scraper-lite`** via `scripts/reddit_via_apify.sh <competitor> month 50` — preferred when WebFetch/browser are blocked from reddit.com (which is common). Returns structured post + comment JSON.
2. **Reddit JSON endpoints** via WebFetch (no auth): `https://www.reddit.com/search.json?q=<competitor>&sort=new&t=year&limit=100` — works in some environments, 401/403 in others.
3. **Google `site:reddit.com` search** via Chrome + `get_page_text` — proxy fallback. Returns titles + snippets + comment counts, not full bodies.
4. **Targeted subreddit search** for relevant subs (see `references/research-sources.md` for the catalog by vertical) — same options as above, scoped per subreddit.
5. **Comment trees** for top 5 threads: Apify actor returns these inline; JSON path uses `https://www.reddit.com/r/<sub>/comments/<id>.json`.

**Review sites**: G2, Capterra, Software Advice, GetApp, TrustRadius, SourceForge.

**Technique**: Chrome-navigate to the review page, filter to 1- and 2-star reviews (those carry real complaint signal — 5-star reviews are often solicited and generic). Extract verbatim review text via `javascript_tool` selector, capture reviewer title/role and date.

**App store reviews** (for mobile products): Chrome-navigate to the App Store and Google Play listings. Filter to recent low-rated reviews. These often surface reliability issues that web reviews miss.

**Good signal**: a theme that recurs across 3+ independent posters within the lookback window. Title and recency matter — a K-12 IT director complaining last month > a random anonymous review from 2022.

### 4. Product launches & roadmap

**Sources**: competitor's `/blog/category/product` or `/changelog` or `/release-notes` or `/whats-new` pages; their YouTube channel (demo videos often reveal features before the blog); Product Hunt; beta announcements.

**Technique**: try those URL patterns in Chrome. If none exist, scrape the blog index and filter for "launch", "introducing", "now available", "shipped". Pull the date from the post.

For roadmap signal: CEO/CPO conference talks (search YouTube), webinar recordings, investor decks (if public), job postings referencing specific product areas.

**Good signal**: dated launches with a clear feature description and customer-visible change.

### 5. Executive & team changes

**Sources**: LinkedIn, Crunchbase, the competitor's `/about` or `/team` page, press releases, TheLayoff.com (rumors but useful directional signal).

**Technique** (Chrome-heavy):
1. LinkedIn company page → "People" tab → sort by "Recently joined" and "Recently left"
2. Check specific senior roles (CRO, VP Sales, VP Product, CPO, CTO, VP CS) for changes
3. Search news for `"<competitor>" "named" OR "appointed" OR "joins" OR "departs"`
4. Look at the competitor's own `/about` page via Wayback to diff against the live page

**Good signal**: departure of named leadership (especially customer-facing: CRO, VP CS, head of support), replacement by someone with a markedly different background, or a hiring push in a specific area (lots of new SDR hires = top-of-funnel push; new ML/AI hires = AI pivot).

### 6. Hiring signal (job postings)

**Sources**: LinkedIn Jobs, Indeed, the competitor's own `/careers` page, Otta, Y Combinator Work at a Startup (for funded startups).

**Technique**: Chrome-navigate to their careers page, pull all open roles with titles + locations + dates posted. Also search LinkedIn Jobs for `"<competitor>"`. Categorize: engineering / sales / CS / marketing / ops / exec.

**Good signal**:
- Sudden growth in a category (10 new SDR roles = aggressive pipeline push)
- Specific technical roles (ML engineer, security engineer, platform engineer) reveal where product is going
- Sales roles by geography reveal market expansion
- Removal of roles that were posted last quarter = hiring freeze or strategy change

### 7. Funding, corporate events, and public financials

**Sources**: Crunchbase, PitchBook (if you have access), SEC filings (public companies), press wires, Pitchbook Discover.

**Technique**: search `"<competitor>" funding OR acquires OR acquired OR Series OR IPO`. For public companies, check SEC EDGAR for 10-K and 10-Q filings — the "risk factors" and "competition" sections often name rivals and strategy.

**Good signal**: new funding (fuels the sales machine), layoffs (distressed = opportunity), acquisition (disruption to their customer base), IPO filing (priorities shift to revenue growth, pricing may change).

### 8. Customer wins and losses

**Sources**: the competitor's `/customers` or `/case-studies` page; press releases; news searches for `"<district/customer> chose <competitor>"` or `"<district/customer> switches to <competitor>"`; the *reverse* search for `"switches from <competitor>"` or `"replacing <competitor>"`.

**Technique**:
- List every named customer on their site (scrape the logos section via Chrome + `javascript_tool`)
- Search for recent district/customer news mentioning them
- **Reverse search** — who's switching AWAY from them? This is gold for objection handling

**Good signal**: named customer with date and a "why they picked us" quote (their marketing) or "why they left them" signal (ours).

### 9. Security, legal, and regulatory

**Sources**: news, SEC filings, state AG offices (for data breaches), the competitor's trust/security pages.

**Technique**: search `"<competitor>" lawsuit OR breach OR incident OR settlement OR investigation`. Check StudentPrivacyPledge signatories (for edu) and SOC 2 / ISO 27001 announcements.

**Good signal**: confirmed security incident, data breach, lawsuit, or regulatory action in the last year. Use **only if confirmed** — rumored incidents damage the rep's credibility.

### 10. Partnerships & integrations

**Sources**: competitor's `/integrations` or `/partners` page, press releases, partner marketplaces (Salesforce AppExchange, Google for Education partners, Microsoft Education partners, Clever Library, ClassLink Marketplace).

**Technique**: Chrome-navigate and enumerate. Compare to our own partner list — gaps are both weaknesses (they integrate with something we don't) and opportunities (we have an integration they don't).

**Good signal**: new partnerships announced recently, or strategic integrations that reveal product direction (e.g., a new SSO integration = moving upmarket).

### 11. Marketing + GTM motion

**Sources**: their website, LinkedIn company posts, webinar pages, conference sponsorship lists, Google ads (search their brand term), SEO ranking (SEMRush / Ahrefs if available).

**Technique**:
- List their webinars and public events — topics reveal messaging priorities
- Search LinkedIn for recent posts from their marketing/sales leaders
- Do a "site:<competitor>.com" search with keywords like "roi", "calculator", "case study" to see where they're investing in content

**Good signal**: new positioning language, new category they're claiming, new persona they're targeting (reveals market-expansion intent).

### 12. Mobile app & product quality signals

**Sources**: App Store and Google Play reviews, BrowserStack-style app download metrics (if available), their status page (`status.<competitor>.com`), DownDetector.

**Technique**:
- Chrome-navigate to App Store / Play Store listings. Pull ratings, review count, recent 1- and 2-star reviews.
- Check their status page for recent incidents
- DownDetector search for outage reports

**Good signal**: recent downward trend in mobile ratings, concentrated outage reports, recurring reliability complaints.

## Workflow

Run the research in parallel waves. Don't do everything serially.

### Wave 1 (fire all in one turn)
Launch in parallel:
- Press/news searches (dim. 1)
- Competitor's own blog, press, pricing, customers, careers, integrations pages (dims. 1, 2, 4, 6, 8, 10) — multiple Chrome navigates + `get_page_text`
- Reddit JSON search (dim. 3) via WebFetch
- LinkedIn company page via Chrome (dims. 5, 6)
- Review sites discovery via WebSearch (dim. 3)
- Wayback Machine snapshot of pricing page, 6 months ago (dim. 2)

### Wave 2 (based on Wave 1 results)
- Deep-fetch review pages found in Wave 1 — filter to 1–2 stars, extract verbatim
- Deep-fetch top 5 Reddit threads by score
- Follow-up on specific moves found in Wave 1 (e.g., if they announced an acquisition, dig into the acquired company)
- App Store / Play Store reviews if they have a mobile product

### Wave 3 (synthesis)
- Cluster findings by dimension
- Rank by impact-on-deals (would a rep bring this up on a call?)
- Cross-reference: anything mentioned in 2+ sources becomes "confirmed"; single-source claims get labeled as such
- Build the talking points and objection handlers (see next section)

### Wave 4 (write)
Save to `./battlecards/<competitor>-YYYY-MM-DD.md`. If `compare_to` was provided, also save `./battlecards/<competitor>-delta-YYYY-MM-DD.md` highlighting only the changes.

## Synthesis: from research to talking points

A good talking point has three parts:
1. **If they say** — the prospect statement. Phrase it in the prospect's voice, not ours.
2. **Say** — the rep's response, in spoken English. No jargon. Includes a specific, citable claim.
3. **Why** — the source. The rep may need to back it up.

**Template**:
> **If they say**: "We're looking at ParentSquare because it's the market leader."
> **Say**: "They're well-known, that's true. The question for your district is which leader wins in three years. Their public 1-star reviews on Capterra from the last six months consistently flag onboarding complexity and parent-account issues — things that bite after the contract is signed. What we'd want to understand is how important a smooth first year is to you."
> **Why**: Capterra reviews from [date] and [date]; specific quotes in our complaints section.

Build **3–5 talking points** that cover the most likely prospect statements. Add **2–4 objection handlers** for the toughest questions (where the competitor genuinely beats us). Don't pad — the rep will only read the first 5 to 7.

## Reddit Pulse synthesis

Reddit returns a mess of posts. Distill into three buckets for the battlecard's **Reddit Pulse** section:

1. **Pain points / complaints** — themes that appear in multiple posts. Rank by recency + upvotes + relevance of subreddit (r/k12sysadmin beats r/Teachers for IT buyer personas, and vice versa for classroom buyer personas). Include verbatim quotes.
2. **Feature requests / workarounds** — users describing what they wish existed, or hacks they've built. These reveal unmet needs (positioning gold) and integration gaps.
3. **Praise / what's working** — be honest here. If users love something, the rep needs to know so they don't walk into a "but ParentSquare does X well" and fumble. The answer to praise is to acknowledge + pivot, not deny.

Pull from the top 5 most-discussed threads (by comment count) in the last 30 days (or the lookback window). If fewer than 5 substantive threads exist, say so — thinness of discussion is itself a data point.

**Every quote must have**: subreddit, post age (or date), comment count (as signal strength), and a link. If using the Apify path, the actor returns this metadata inline. If using the Google-proxy path, capture what the snippets provide.

## Output: the full battlecard template

See `references/battlecard-template.md` for the complete template with every section. Short version:

```markdown
# Battlecard: <Competitor> — YYYY-MM-DD

_Scanned: <sources>. Focus: <focus or general>. Depth: <depth level>._

## TL;DR
Three bullets. What's changed that a rep needs to know today.

## Recent moves
Dated bullets with source and implication.

## Pricing tear-down
Table: tier | cost | min units | contract terms | promos expiring | notes. Sourced.

## What users are complaining about
Themes with recurrence count and verbatim quote + source.

## Reddit Pulse
Three subsections: Pain points, Feature requests & workarounds, Praise. Each with verbatim quotes, subreddit, age, comment count, link. See "Reddit Pulse synthesis" section above for methodology.

## Recent feature launches / roadmap
Dated launches, our equivalent (or gap), source.

## Executive & team changes
Named departures / arrivals, dates, why it matters.

## Hiring signal
Role categories, notable patterns, implications.

## Customer movement
Who just picked them. Who just left them (gold). Sources.

## Integrations & partnerships
New partners, ecosystem gaps.

## Security / legal / regulatory
Confirmed incidents only. Skip if nothing real.

## Talking points for sales (3–5)
If they say → Say → Why.

## Objection handlers (2–4)
Objection → Response → Evidence.

## Where we beat them
Concrete, sourced.

## Where they beat us (be honest)
Concrete, sourced, with pivot.

## Switching-cost playbook
If the prospect is currently on them, here's the migration story.

## Qualification signals
Red flags that this is a low-probability deal against them.

## Timing triggers
Events that make now the right time to displace.

## Sources
Everything cited, with dates.

## Delta since last battlecard (if compare_to provided)
What changed.
```

## Formatting principles

- **Specificity over volume.** 3 concrete sourced insights beats 15 generic ones.
- **Quote users in their own words.** Verbatim review text, verbatim Reddit quotes. Paraphrases lose credibility and force the rep to reconstruct.
- **Every claim gets a source URL and a date.** No source = don't include it. Old source (>12 months for fast-moving categories) = label it as historical.
- **Write talking points in spoken English.** If it reads like a deck slide ("leveraging our differentiated value proposition"), rewrite it.
- **Be honest about where they win.** Reps walking in with a one-sided battlecard get destroyed when the prospect raises the thing you didn't prepare them for.
- **Confidence labels**: `[confirmed]` (2+ independent sources), `[single-source]` (one source, named), `[rumor]` (uncorroborated). Default is confirmed; label the others.
- **Rank by recency within each section.** Most recent first. A rep scanning at 9am for a 10am call reads top-down.

## Edge cases

- **Quiet competitor / nothing recent**: say so explicitly. "No material moves in the last N days; last signal was <date>: <summary>." Don't pad.
- **Reddit returns empty via JSON**: fall back to Chrome search UI; check specific subreddits directly (even if search is dry). A competitor may have zero `/search` hits but active threads in a niche sub.
- **Review sites are thin or old**: note it. "Review data is sparse — most recent review is 8 months old." That itself is a signal (product may have stabilized, or user base may have churned).
- **Paywalled source**: skip it. A rep can't cite what they can't read.
- **Rumor vs. fact**: flag with `[rumor]`. Do not promote rumors to confirmed without independent sourcing.
- **Too much signal**: dedupe by theme, keep the most recent and most-sourced example per theme.
- **Focus returns little**: widen briefly. Don't invent news to fit the focus — note honestly.
- **LinkedIn rate-limits or requires login**: use their public company page (doesn't require login for basic company data); for individual profile data, skip rather than force.
- **Competitor pivots mid-scan** (e.g., you find they just announced a major acquisition during Wave 1): stop, re-plan. The battlecard needs to be built around the new reality.
- **Delta mode with no previous battlecard**: fall back to standard mode, note that no prior exists.
- **Non-English sources**: include if translation is straightforward and the content is high-signal. Otherwise skip.

## Bundled resources

See these for deeper guidance:

- `references/research-sources.md` — exhaustive catalog of sources by dimension, with URL patterns and what to look for
- `references/reddit-playbook.md` — Reddit-specific techniques: JSON endpoints, subreddit catalog by vertical, comment-tree parsing, rate-limit handling
- `references/battlecard-template.md` — the full battlecard template with all sections and placeholder examples
- `references/dimension-checklist.md` — 12-dimension checklist with "did you cover this?" questions

## Why this skill goes wide

Most competitive intel is shallow — a rep asks "what's the latest on ParentSquare?" and gets a web search summary. That misses the things that actually win deals:

- A departing VP of CS signals churn risk to their customers — use it to go sniff that customer base
- A hiring push for SDRs signals they're spraying top-of-funnel — use it to warn your AEs about pipeline noise
- A one-star review from a district IT director naming the exact feature your product does better is the most effective talking point that exists
- A Wayback diff showing they quietly raised prices 20% last quarter is a procurement weapon

The twelve-dimension approach exists because deals are lost on dimensions reps didn't prepare for. Covering all twelve — and labeling what's thin — is what makes this useful at ARR scale, not just "prep for Tuesday's call".
