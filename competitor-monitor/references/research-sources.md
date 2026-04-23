# Research sources catalog

A deep index of where to look for each of the 12 competitive-intelligence dimensions. Use this when the SKILL.md workflow tells you to research a dimension and you need specific URLs / patterns.

## 1. Recent moves (press & news)

### Primary
- `https://www.google.com/search?q=<competitor>+news&tbm=nws&tbs=qdr:m` — Google News, last month
- `https://news.google.com/search?q=<competitor>` — Google News aggregate
- `<competitor>.com/press/` or `/news/` or `/media/` — their own press page
- `https://www.prnewswire.com/search/all/?keyword=<competitor>` — PR Newswire
- `https://www.businesswire.com/portal/site/home/?ndmViewId=news_view&newsId=search&query=<competitor>` — BusinessWire

### Industry-specific (K-12 / edu)
- [EdSurge](https://www.edsurge.com) — search "<competitor>"
- [THE Journal](https://thejournal.com) — K-12 tech news
- [EdWeek Market Brief](https://marketbrief.edweek.org) — gated but high-signal
- [District Administration](https://districtadministration.com)
- [eSchool News](https://www.eschoolnews.com)

### Industry-specific (other)
- HR tech: HR Dive, HR Executive
- Sales tech: SalesHacker, SaaStr
- Dev tools: Hacker News, The New Stack, InfoQ
- Healthcare: Healthcare IT News, Fierce Healthcare
- Fintech: Finextra, The Paypers

### Noise to filter
- Content-farm sites that repost PR verbatim with no new info
- "Top 10" listicles from affiliate marketers
- Sponsored content (check for "Sponsored" or "Ad" labels)

---

## 2. Pricing

### Direct
- `<competitor>.com/pricing` — always check first
- `<competitor>.com/plans` or `/packages`
- Sales FAQ pages (sometimes leak per-seat numbers)

### Indirect
- G2 pricing section (has negotiated numbers vendors hide)
- Capterra pricing section
- GetApp pricing
- Software Advice pricing
- AWS Marketplace listing (`aws.amazon.com/marketplace/search?searchTerms=<competitor>`)
- Azure Marketplace
- Google Cloud Marketplace

### Government / procurement (K-12 / edu specifically)
- Sourcewell: `https://www.sourcewell-mn.gov` — approved vendor pricing
- TIPS (The Interlocal Purchasing System): `https://www.tips-usa.com`
- Remcsave.org: `https://www.remcsave.org/catalog` — Michigan REMC catalog
- State-specific procurement portals (CA, TX, FL, NY)
- BuyBoard National Purchasing Cooperative

### Historical (Wayback Machine)
- `http://web.archive.org/web/*/` + competitor pricing URL
- Compare snapshots from 6 months, 12 months, 24 months ago
- Diff reveals: price increases, tier restructuring, removed discounts, new minimums

### Pricing tear-down table format
When writing the battlecard's pricing section, use this table:

| Tier | List price | Min units | Contract term | Onboarding fee | Active promos | Source |
|---|---|---|---|---|---|---|
| e.g. "Communicate" | $3,000/yr base | 2,000 students | 1 or 2-yr | $1,500 min | 50% off onboarding by Jun 30 | [Pricing page](url) |

---

## 3. User complaints

### Reddit
See `reddit-playbook.md` for the full methodology.

### Review sites (priority order — check all)
1. **G2**: `g2.com/products/<slug>/reviews` — filter to 1–2 star via URL params
2. **Capterra**: `capterra.com/p/<id>/<slug>/reviews` — has "Pros/Cons" extracted per review
3. **Software Advice**: `softwareadvice.com/k-12/<slug>-profile/reviews/` (or relevant category)
4. **GetApp**: `getapp.com/<category>/a/<slug>/reviews/`
5. **TrustRadius**: `trustradius.com/products/<slug>/reviews`
6. **SourceForge**: `sourceforge.net/software/product/<slug>/`
7. **Trustpilot** (consumer-facing products): `trustpilot.com/review/<domain>`

### Extraction technique
Chrome-navigate to review URL. Use `javascript_tool` with a selector pattern:
```js
Array.from(document.querySelectorAll('[class*="review"]')).map(r => ({
  rating: r.querySelector('[class*="star"]')?.textContent,
  date: r.querySelector('[class*="date"]')?.textContent,
  title: r.querySelector('h3, h4, [class*="title"]')?.textContent,
  body: r.querySelector('[class*="body"], p')?.textContent,
  reviewer: r.querySelector('[class*="reviewer"]')?.textContent
}))
```
Tune selectors per site (they differ). Test on one review before pulling all.

### App store reviews
- **Apple App Store**: `https://apps.apple.com/us/app/<slug>/id<id>` — scroll to reviews, sort by "Most Recent"
- **Google Play**: `https://play.google.com/store/apps/details?id=<package>&showAllReviews=true`

Use Chrome to navigate and extract. App store reviews often surface reliability issues faster than web reviews.

### What to look for
- **Themes that recur 3+ times** across independent posters in the lookback window
- **Recent posts (<90 days) with senior titles** (Director, VP, Superintendent, CIO)
- **Specific, reproducible complaints** ("the photo uploader hangs above 5MB") beat vague ones ("it's buggy")

### What to discard
- Single-point complaints without recurrence
- Reviews that read like competitor plants (check for unnatural phrasing, competitor-product name-drops)
- Very old reviews (>12 months) unless no recent reviews exist

---

## 4. Product launches & roadmap

### Primary
- `<competitor>.com/blog/category/product` — or `/releases`, `/changelog`, `/whats-new`, `/release-notes`
- Their YouTube channel — demo videos
- Their webinar archive

### Secondary
- Product Hunt — search for competitor
- BetaList (for early-stage products)
- Conference talk abstracts (look for CEO/CPO keynotes)
- Investor decks (if publicly filed via SEC or press release)

### Detection technique
Navigate to their blog index. Use `javascript_tool` to filter posts by keywords:
```js
Array.from(document.querySelectorAll('article, [class*="post"]'))
  .filter(p => /introducing|launching|now available|shipped|release/i.test(p.textContent))
  .map(p => ({title: p.querySelector('h2,h3')?.textContent, date: p.querySelector('[class*="date"],time')?.textContent, href: p.querySelector('a')?.href}))
```

### Roadmap signals (forward-looking)
- "Coming soon" language on product pages
- Beta program announcements
- Job postings for specific product areas (e.g., "Senior Engineer, Attendance Platform")
- CPO / CEO public statements on podcasts / conference stages
- Acquisitions (usually telegraph direction)

---

## 5. Executive & team changes

### LinkedIn (Chrome-navigate)
- `https://www.linkedin.com/company/<slug>/people/` — sorted by recent activity
- Filter by department (LinkedIn's sidebar filters): Sales, Product, Engineering, Customer Success, Marketing
- "Recently joined" vs. "Recently left" — LinkedIn sometimes surfaces both

### Named-role tracking
Check for changes in these roles specifically (sorted by impact to us):
- **CRO / VP Sales** — sales strategy shifts
- **VP Customer Success / VP CX** — churn risk signal
- **CPO / VP Product** — product direction shifts
- **CEO / Founder** — full strategy reset
- **CFO** — financial stress / IPO prep signal
- **CMO / VP Marketing** — positioning shifts
- **Head of Partnerships** — ecosystem strategy

### Sources for departures
- LinkedIn "Experience" → end date on their profile
- [TheLayoff.com](https://www.thelayoff.com) — rumors but directional
- Press releases (layoffs usually get announced)
- Glassdoor reviews mentioning leadership turnover

### News search
- `"<competitor>" "named" OR "appointed" OR "joins" OR "departs" OR "promoted"`
- `"<competitor>" "former" OR "ex-" CEO OR CRO OR CTO`

---

## 6. Hiring signal

### Primary sources
- `<competitor>.com/careers` or `/jobs` — their own postings
- LinkedIn Jobs: `linkedin.com/jobs/search/?f_C=<company-id>` — all their active postings
- Indeed: `indeed.com/cmp/<company>/jobs`
- Glassdoor jobs page
- Otta: for tech startups
- Y Combinator Work at a Startup (for YC-funded)
- AngelList / Wellfound

### Extraction
Chrome-navigate to careers page. Extract all roles with title, location, date posted, department. Look for:
- **Velocity**: 20 new postings in the last month = aggressive growth
- **Category concentration**: 10 new SDR roles = TOFU push; 5 new ML engineer roles = AI investment
- **Geographic expansion**: first hires in a new country/region = market entry
- **Exec backfills**: "VP of X" or "Head of X" openings = leadership gap
- **Disappeared roles**: roles posted 3 months ago that are gone now, without an announcement = either hired or quietly cancelled (the latter = hiring freeze)

### Wayback diff
Compare `<competitor>.com/careers` against Wayback snapshots from 1, 3, 6 months ago to see what opened / closed.

---

## 7. Funding & corporate events

### Primary
- [Crunchbase](https://www.crunchbase.com) — free tier shows funding rounds and dates
- [PitchBook](https://pitchbook.com) — if you have access
- [SEC EDGAR](https://www.sec.gov/edgar) — public companies, 10-K / 10-Q / 8-K filings
- Press releases (fundings are announced)

### Public company filings
- **10-K**: annual report. The "Competition" and "Risk Factors" sections name rivals and strategy concerns.
- **10-Q**: quarterly update. Watch for guidance changes.
- **8-K**: material events. Acquisitions, leadership changes, restatements.
- **DEF 14A** (proxy statement): executive comp, which reveals performance metrics the board watches.

### Private company signals
- Crunchbase News
- AXIOS Pro
- The Information
- TechCrunch — funding coverage

### What to extract
- Funding amount, round, lead investor, date
- Use-of-funds language (often reveals strategy)
- Valuation if disclosed
- Investor names (if a strategic investor, it tells you something)
- Runway inference (from round size and burn rate if known)

---

## 8. Customer wins and losses

### Their wins (their marketing)
- `<competitor>.com/customers` — logo wall
- `/case-studies` — detailed wins with quotes and metrics
- Press releases announcing specific customer signings
- Their annual report / blog retrospective posts

### Extraction
Navigate to /customers. Use `javascript_tool` to grab all logo alt-text and URLs:
```js
Array.from(document.querySelectorAll('img[alt], [class*="logo"]'))
  .map(el => el.alt || el.getAttribute('aria-label') || el.textContent.trim())
  .filter(t => t && t.length < 100)
```

### Their losses (our opportunities)
**This is the highest-value research in this section.** Customers who left them become talking points.

Search techniques:
- `"<customer>" "moving from <competitor>"` or `"replacing <competitor>"` or `"switched from <competitor>"`
- `"<competitor>" "no longer using"` or `"we left"`
- Industry news: districts announcing platform changes often mention what they're leaving
- School board meeting minutes (for edu) — often surface vendor change decisions
- Reddit complaint threads sometimes name the replacement

### Reverse search technique
For the vertical you're in, identify 5–10 districts/customers known to have churned and research why. The themes that emerge become objection-handler material.

---

## 9. Security, legal, regulatory

### Security
- `<competitor>.com/security` or `/trust` — their security page
- SOC 2 / ISO 27001 / FedRAMP / StateRAMP compliance claims
- [HasMyDataBeenPwned](https://haveibeenpwned.com) — breach database
- [vpnMentor](https://www.vpnmentor.com/blog/?s=<competitor>) — breach research
- [TechCrunch Security](https://techcrunch.com/category/security/) — breach coverage
- State AG office breach notifications

### Legal
- [PACER](https://pacer.uscourts.gov) — federal court filings (paid, but cheap)
- [CourtListener](https://www.courtlistener.com) — free federal cases
- State court search
- News search: `"<competitor>" lawsuit OR litigation OR sued`

### Regulatory (edu-specific)
- [StudentPrivacyPledge.org](https://studentprivacypledge.org) — signatory list
- FERPA compliance claims
- COPPA compliance for under-13 products
- State data privacy laws (NY Ed Law 2-d, etc.)

### Use carefully
Cite only confirmed incidents with legal filings or verified reporting. "Rumored breach" hurts your rep's credibility more than it hurts the competitor.

---

## 10. Partnerships & integrations

### Primary
- `<competitor>.com/integrations` — their own list
- `/partners` — strategic partners

### Partner marketplaces
- Salesforce AppExchange
- HubSpot App Marketplace
- Google Workspace Marketplace
- Microsoft AppSource
- Slack App Directory
- Zoom Marketplace
- Zapier app directory

### Industry-specific (K-12)
- [Clever Library](https://www.clever.com/app-gallery)
- [ClassLink Marketplace](https://launchpad.classlink.com)
- [Google for Education partner directory](https://edu.google.com/why-google/our-commitment/apps/)

### What to look for
- New integrations announced in the last 90 days
- Strategic partnerships (often press-released)
- Integrations they *don't* have (opportunity for positioning)
- Tech stack implied by integrations (e.g., Salesforce integration = enterprise-oriented)

---

## 11. Marketing & GTM

### Content inventory
- Their blog category taxonomy (reveals where they invest content)
- Their webinar archive — topics and frequency
- Their conference sponsorships (look at ISTE, ASU-GSV, ERB, etc. sponsor lists for edu)
- Their podcast (if they have one)
- Their email newsletter signup — subscribe to monitor

### Paid media signals
- Google ads on their brand term (competitive intel tools: SpyFu, SEMRush)
- LinkedIn Ads (LinkedIn's Ad Library shows current campaigns)
- Facebook Ad Library: `facebook.com/ads/library/`
- YouTube pre-roll patterns

### SEO / traffic
- SimilarWeb (free tier) for traffic estimates
- Ahrefs / SEMRush (paid) for keyword rankings and content gaps
- Their sitemap.xml — reveals all public pages
- "site:<competitor>.com" search with keywords

### Social signals
- LinkedIn company posts — engagement rate and themes
- LinkedIn posts from their leadership (CEO, CPO, CRO)
- Twitter/X activity
- YouTube channel subscriber count and video view patterns

---

## 12. Mobile & product quality

### App store listings
- Apple App Store: `apps.apple.com/us/app/<slug>/id<id>`
- Google Play: `play.google.com/store/apps/details?id=<package>`

### Key metrics
- Rating distribution (4.8 vs 3.2 is a big story)
- Review count (volume = user base size proxy)
- Recent 1–2 star review velocity
- Response to reviews (do they respond, or ignore?)
- Last updated date (are they actively developing?)

### Status & reliability
- `status.<competitor>.com` — official status page
- `<competitor>statuspage.io` pattern (Statuspage.io hosted)
- [DownDetector](https://downdetector.com/status/<competitor>/) — user-reported outages
- [IsItDownRightNow](https://www.isitdownrightnow.com)

### What to look for
- Recent major outages (cite with dates)
- Downward rating trend
- Responsiveness gap (slow fixes of reported issues)

---

## Cross-cutting: Wayback Machine

The Wayback Machine is underused. Useful for:
- Pricing history (diff pricing pages over time)
- Feature page diffs (what they removed from their feature list is a signal)
- Customer logo wall diffs (who came off the wall)
- /careers history (hiring patterns)
- /team or /about diffs (who left without a press release)

URL: `http://web.archive.org/web/*/<target-url>`

Pick 3 snapshots: 3 months, 6 months, 12 months. Diff manually or with a script.

---

## Cross-cutting: LinkedIn (public pages only)

Without login, you can access:
- Company page (public)
- Company "About" and general info
- Some public posts

With login (user's own session via Chrome):
- People tab
- Jobs page
- Full post history of public posts
- Individual profiles of employees

Never auto-login. If LinkedIn blocks or requires login, skip gracefully.
