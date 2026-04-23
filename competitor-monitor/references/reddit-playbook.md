# Reddit playbook

Reddit is systematically under-indexed by web search engines. The competitive intelligence signal there is high but requires direct navigation. This playbook covers the techniques.

## Token security

- **Never commit** `~/.apify_token` or any file containing the raw token. Keep it chmod 600 in the user's home directory, outside any git-tracked path.
- **Never paste** the token into a battlecard, skill file, PR, issue, or chat message that's stored or shared.
- **If the token is ever exposed** (pasted in chat, committed, shared over email), rotate it immediately at [console.apify.com/account/integrations](https://console.apify.com/account/integrations). Assume exposed = compromised.
- The helper script reads from env or from `~/.apify_token` — there's no need for the token to appear anywhere else.

## Why Reddit matters

- Users complain unfiltered — no review-site moderation, no solicitation bias
- Buyers ask each other for recommendations ("thinking of switching from X to Y — thoughts?")
- Employees of competitors occasionally post (check for edited-to-redact-detail patterns)
- Ex-employees sometimes post on r/cscareerquestions or r/sales about internal dysfunction
- Feature requests get debated in public — reveals roadmap pressure

## Access paths (priority order)

In many hosted environments, `reddit.com` is blocked by browser safety policies and WebFetch. Try in this order:

### Tier 1 — Apify `trudax/reddit-scraper-lite` (preferred)

Bundled helper: `scripts/reddit_via_apify.sh <competitor> [time_range] [max_items]`

**Setup (one-time)**:
```bash
# Generate a token at https://console.apify.com/account/integrations
echo 'apify_api_YOURKEY' > ~/.apify_token
chmod 600 ~/.apify_token
```

Or set `APIFY_TOKEN` as an environment variable. The script reads `$APIFY_TOKEN` first, falling back to `~/.apify_token`. **Never hardcode the token in a skill file, battlecard, committed script, or git-tracked location.**

**Usage**:
```bash
# Search all of Reddit for "ParentSquare" in the last month, pull up to 50 posts
scripts/reddit_via_apify.sh "ParentSquare" month 50 > /tmp/reddit_raw.json

# Or pipe straight into jq/python for filtering
scripts/reddit_via_apify.sh "ParentSquare" month 50 | python3 -c "
import json, sys
posts = json.load(sys.stdin)
for p in sorted(posts, key=lambda x: x.get('numberOfComments', 0), reverse=True)[:5]:
    print(f\"[{p.get('communityName')}] {p.get('title')} — {p.get('numberOfComments')} comments, {p.get('upVotes')} upvotes\")
    print(f\"  {p.get('url')}\")
    print(f\"  {(p.get('body') or '')[:300]}\")
    print()
"
```

**Actor input knobs** (passed by the script — edit the script if you need different behavior):
- `searches`: query strings (array)
- `sort`: `new` | `relevance` | `top` | `comments`
- `time`: `hour` | `day` | `week` | `month` | `year` | `all`
- `maxItems` / `maxPostCount`: cap total posts
- `maxComments`: per-post comment fetch cap (default 10 in the script)
- `skipComments`: true to skip comment-tree fetching (faster, less signal)
- `proxy`: the script uses Apify's proxy by default (recommended; avoids IP-based rate limits)

**Response shape** — the actor returns an array of post objects. Key fields:
- `title`, `body`, `url`, `permalink`
- `communityName` (e.g., "k12sysadmin") — **not** `subreddit` like the raw JSON API
- `author`, `upVotes`, `downVotes`, `numberOfComments`
- `createdAt` (ISO timestamp) — easier than Unix epoch
- `comments`: array of `{author, body, upVotes, createdAt}` (populated unless `skipComments: true`)

**Cost**: Apify's free tier covers small runs. Each run consumes actor compute units — check your plan at console.apify.com. For a 50-post pull with 10 comments each, expect ~0.01–0.05 CUs.

### Tier 2 — Reddit JSON endpoints (no auth)

Reddit exposes most public content as JSON. Append `.json` to almost any Reddit URL.

### Search across all of Reddit
```
https://www.reddit.com/search.json?q=<competitor>&sort=new&t=year&limit=100
```

Parameters:
- `q` — search query (URL-encode spaces as `+` or `%20`)
- `sort` — `new` (most recent), `relevance` (default), `top`, `comments` (most-commented)
- `t` — time range: `hour`, `day`, `week`, `month`, `year`, `all`
- `limit` — 1 to 100

### Search within a specific subreddit
```
https://www.reddit.com/r/<subreddit>/search.json?q=<competitor>&restrict_sr=on&sort=new&t=year
```

`restrict_sr=on` confines the search to that subreddit.

### Get a post + its comment tree
```
https://www.reddit.com/r/<subreddit>/comments/<post_id>.json
```

Returns an array: `[post_data, comment_tree]`. Comment tree is nested — flatten recursively for full threads.

### Get a subreddit's recent posts
```
https://www.reddit.com/r/<subreddit>/new.json?limit=100
```

Useful when you have a relevant subreddit but the competitor name doesn't appear in search — they may be referred to by slang or product name.

### User post history
```
https://www.reddit.com/user/<username>/submitted.json
https://www.reddit.com/user/<username>/comments.json
```

Useful if you find a high-signal commenter and want to see their other posts (validates they're a real practitioner, not a shill).

## Parsing the JSON

Top-level shape for search:
```json
{
  "data": {
    "children": [
      {
        "kind": "t3",
        "data": {
          "title": "...",
          "selftext": "...",
          "subreddit": "...",
          "author": "...",
          "score": 42,
          "num_comments": 15,
          "created_utc": 1776940000,
          "url": "...",
          "permalink": "/r/sub/comments/abc123/...",
          "id": "abc123"
        }
      }
    ]
  }
}
```

For each result, extract:
- `title`, `selftext` (post body), `subreddit`
- `author`, `score`, `num_comments`
- `created_utc` (Unix timestamp — convert to date)
- `permalink` (prepend `https://www.reddit.com`)
- `id` (for fetching comments)

## Comment tree parsing

Comment replies nest under `data.replies.data.children`. A comment looks like:
```json
{
  "kind": "t1",
  "data": {
    "author": "...",
    "body": "...",
    "score": 12,
    "created_utc": 1776940000,
    "replies": { "data": { "children": [...] } }
  }
}
```

Flatten recursively. For battlecard purposes, top-level comments and direct replies usually carry the signal — deep threads often devolve.

## Ranking signal

Within a set of Reddit results, rank by:

1. **Recency** (weight heavily — months-old complaints may have been fixed)
2. **Subreddit relevance** (r/k12sysadmin = gold for edu; r/Parenting = mixed)
3. **Score** — `>10` upvotes suggests the complaint resonated with others
4. **Comment count** — `>10` comments means active discussion
5. **Author signals** — flair, post history (is this a real practitioner?), account age

Quality floor: don't quote anything under `score=3` and `num_comments=2` unless the content is exceptional.

## Subreddit catalog by vertical

### K-12 edu
- **r/k12sysadmin** — K-12 IT directors and admins. **Highest signal** for district tech decisions.
- **r/Teachers** — classroom teachers. Signal on parent-facing tools and classroom products.
- **r/education** — broad, mixed signal. Filter hard.
- **r/principals** — building administrators.
- **r/edtech** — often marketing-heavy, low signal.
- **r/specialed** — special education specifics.

### Higher ed
- **r/AskAcademia** — faculty and staff
- **r/Professors** — faculty
- **r/college** — student perspective
- **r/gradschool**

### Parents (as buyers for family-facing tools)
- **r/Parenting**
- **r/Teachers** (parents post here about school communication)
- **r/daddit**, **r/Mommit**

### SaaS / enterprise IT
- **r/sysadmin** — IT operations
- **r/msp** — managed service providers
- **r/ITManagers**
- **r/ITCareerQuestions**
- **r/sales**, **r/salesforce** — RevOps and sales teams
- **r/cscareerquestions** — ex-employee complaints occasionally surface

### Vertical-specific
- **r/medicine**, **r/nursing** — healthcare
- **r/Accounting**, **r/FP_and_A** — finance
- **r/humanresources** — HR
- **r/marketing** — MarTech
- **r/devops**, **r/programming** — developer tools

### Discovery technique
If you don't know the right subreddit, search Reddit for the competitor and see which subreddits the results come from. That's your target list.

## Chrome navigation fallback

When JSON endpoints rate-limit (429) or return empty:

1. Navigate to `https://www.reddit.com/search/?q=<competitor>&sort=new&t=year`
2. Extract posts via `javascript_tool`:
```js
Array.from(document.querySelectorAll('[data-testid="post-container"], article'))
  .slice(0, 25)
  .map(p => ({
    title: p.querySelector('h3, h2')?.textContent,
    subreddit: p.querySelector('[data-testid="subreddit-name"], a[href*="/r/"]')?.textContent,
    body: p.querySelector('[data-click-id="text"] p')?.textContent?.slice(0, 500),
    score: p.querySelector('[data-testid="vote-arrows"]')?.textContent,
    age: p.querySelector('time, [data-testid="post-age"]')?.textContent,
    href: p.querySelector('a[data-click-id="body"]')?.href
  }))
```

Reddit's DOM structure changes — test your selectors first and adjust.

## Rate limits

- JSON endpoints: ~60 requests/minute from an IP. Space requests if doing many.
- If you hit 429, back off for 60 seconds then retry with a custom user-agent via WebFetch
- Chrome navigation: governed by the browser's own rate, not Reddit's API limit

## Known limitations

- **Deleted posts/comments** show as `[deleted]` — the content is gone. Useful pattern: a thread with many deleted comments often indicates the mods or author removed specific criticism. Investigate parent comments for context.
- **Shadowbanned or low-karma users** may have low-visibility posts — worth reading; often unvarnished
- **Employees astroturfing** is rare on Reddit but happens. Check account age (<30 days is suspicious) and post history (only posts about the company = shill)
- **Brigading** — a thread with suddenly-shifted sentiment may have been linked externally. Check the comment timestamps for clumping.

## What to extract into the battlecard

From Reddit, the battlecard's "complaints" section should have:
1. The theme (2–4 words)
2. How many independent posters mentioned it in the lookback window
3. **One verbatim quote** (the strongest one) with attribution: subreddit, date, score
4. Link to the post

Example:
> **Theme**: Onboarding complexity (seen 4 times across r/k12sysadmin, last 90 days)
> **Quote**: "Spent 3 weeks getting SIS sync to work. Support was slow. Would have been faster to roll our own." — [r/k12sysadmin, 2026-02-15, 34 upvotes](https://www.reddit.com/r/k12sysadmin/comments/...)
