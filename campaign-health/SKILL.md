---
name: campaign-health
description: Daily marketing campaign health check for ClassDojo Districts. Pulls Metabase website traffic for campaign URLs, HubSpot MQL/contact data, and #districts-marketing Slack updates, then outputs a bullet-list summary ready to paste into Slack. Use this skill whenever the user asks for a campaign update, daily marketing check, campaign health, how campaigns are performing, MQL counts, traffic numbers, or says things like "run campaign health", "what's the campaign status", or "give me the marketing update".
---

# Campaign Health

Produces a daily campaign performance snapshot from three sources: HubSpot (email performance + MQLs + pipeline), Metabase (website traffic for campaign URLs), and Slack (#districts-marketing updates). Output is formatted as a Slack-ready bullet list.

## Parameters

- `days` (default: 7) — lookback window for metrics
- `campaign` (optional) — filter to a specific campaign name (e.g. "budget", "canva", "privacy")

## Data Sources & How to Access Them

### 1. HubSpot — Email Performance, MQLs & Pipeline

District marketing email data lives in HubSpot. Use the HubSpot MCP to pull all of the following.

**Email performance** — requires HubSpot Campaigns permission scope:
- Use `get_campaign_analytics` with `requestedData: METRICS` for each active campaign
- Set `startDate` / `endDate` to the lookback window
- Key metrics: sessions, new contacts influenced, open rate, click rate

> ⚠️ **Permission gap:** Campaign-level metrics (open/click rates) are currently blocked on the connected HubSpot app. To fix: HubSpot → Settings → Integrations → Connected Apps → grant **Campaigns** scope. Until then, use contact-level engagement as a proxy (see below).

**Contact-level email proxy** (when campaign permissions are unavailable):
```
search_crm_objects: contacts
filter: hs_email_last_send_date >= [start of period]
properties: hs_email_last_send_date, hs_email_last_open_date, hs_email_last_click_date,
            hs_email_bounce, hs_email_sends_since_last_engagement, hs_email_domain
```
From this, compute: % opened in period, % clicked, bounce count, contacts with 5+ sends no engagement.

**New contacts (MQLs):**
```
search_crm_objects: contacts
filter: createdate >= [start of period]
properties: firstname, lastname, email, createdate, hs_lead_source
```
Report total count and note top lead sources.

**Deals in pipeline:**
```
search_crm_objects: deals
filter: createdate >= [start of period]
properties: dealname, dealstage, amount, createdate
```

### 2. Metabase — Website Traffic for Campaign URLs
Metabase is at `metabase.internal.classdojo.com` (internal — requires VPN or corp network).

Use Chrome to navigate there. Campaign URLs follow the pattern `classdojo.com/districts/*`.

Steps:
1. Navigate to Metabase via Chrome
2. Look for district campaign dashboards (one exists at `/dashboard/1705-district-maps`)
3. Filter page views / sessions to `/districts/` URL paths for the lookback period
4. If no suitable dashboard exists, tag `@QueryCurie` in `#districts-marketing` with: "what were site visits to classdojo.com/districts/* pages in the last [N] days?"

If Metabase is unreachable (VPN not active), note it and continue with other sources.

### 3. Slack — #districts-marketing Updates
Read recent messages from `#districts-marketing` (channel ID: `C08EUP26GTT`).

Look for:
- Campaign launch announcements or recaps
- Webinar/event attendance numbers (e.g. "111 registrants, 43 attendees")
- Content requests or blockers flagged by the team
- Any performance numbers shared in the channel

Also check `#district-marketing-reviews` (C0A87SGEBJN) for content going live.

## Output Format

Format the output as a Slack-ready message with this structure:

```
📊 *Campaign Health — [DATE]* (last [N] days)

*🎯 MQLs & Pipeline*
• New contacts: [N] ([delta vs prior period if available])
• Deals created: [N]
• [Notable deal or lead if any]

*📧 Email Performance*
• [Campaign name]: [sends] sent · [open rate]% open · [CTR]% click
• [Campaign name]: [sends] sent · [open rate]% open · [CTR]% click
• Bounces/unsubs: [N] / [N]
• [Flag any anomaly — e.g. "⚠️ open rate dropped 8pts vs last week"]

*🌐 Website Traffic*
• /districts/* pages: [N] sessions ([delta])
• Top campaign URL: [url] — [N] visits
• [Flag any anomaly]

*📣 Channel Updates*
• [1-2 bullet summary of notable #districts-marketing activity]
• [Any campaigns launching or content going live]

*⚠️ Flags*
• [Anything that needs attention — low traffic, high bounces, missed follow-ups]
```

## Ranking & Flagging Logic

Flag something as ⚠️ when:
- Open rate drops more than 5 percentage points week-over-week
- Bounce rate exceeds 0.5% on a send
- Traffic to a campaign URL drops more than 20% week-over-week
- A team member flagged a blocker or urgent ask in Slack that hasn't been addressed

Keep the output tight — aim for 15-20 bullet points total. This is meant to be scanned in 30 seconds, not read like a report.

## If a source is unavailable

- Metabase unreachable: note "⚠️ Metabase unavailable (VPN?)" and skip traffic/email sections
- HubSpot permission error: note "⚠️ HubSpot campaign data blocked — contact count used as proxy"
- Slack read fails: skip channel updates section

Always produce output even with partial data.
