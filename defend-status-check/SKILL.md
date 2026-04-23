---
name: defend-status-check
description: Pull a live status report for all Defend-strategy districts from Salesforce. Use this skill whenever the user types "/Defend status check", asks about defend district status, wants to see which defend accounts are at risk, asks for a summary of defend account health or renewal status, or wants to know what's happening with defend districts. Always use this skill for any question about the overall state or health of the defend portfolio — don't try to answer from memory or run ad-hoc queries; run the full report.
---

## What this skill does

Generates a live, structured status report for all accounts where `X2025_2026_Strategy__c = 'Defend'`. The report includes:

- **Account status**: health score, renewal status, forecasted renewal date, segment, DPM
- **Last activity**: most recent touch across Tasks, Events, Gong calls, and Partner Engagements
- **Next steps**: pulled from `Key_Takeaways_Next_Steps__c` on the latest engagement

## How to run it

```bash
python3 ~/.claude/skills/defend-status-check/scripts/defend_status.py
```

This script queries Salesforce directly and prints a formatted markdown report. It takes ~15-30 seconds for all queries to complete.

## How to present the results

The script outputs a full markdown report. Present it to the user as-is, then offer to:
- Filter to a specific health score, segment, or DPM
- Show only accounts with no recent activity (no engagement in last 60 days)
- Export to a specific format
- Drill into a specific account

## Key data notes

- **FY records**: Named `FY 25-26 - [Account Name]` -- not all accounts have one yet
- **Accounts without a FY record**: Listed separately at the bottom -- these need attention
- **Next steps field**: Free text from meeting notes; may be blank if no engagements logged
- **Credentials**: Requires a `.env` file with `SALESFORCE_USERNAME`, `SALESFORCE_PASSWORD`, `SALESFORCE_KEY`, and optionally `SALESFORCE_INSTANCE_URL`. Looks for `~/.claude/.env` first, then `~/.env`.

## Setup

```bash
pip3 install simple-salesforce python-dotenv
```

Add to `~/.claude/.env` (or `~/.env`):
```
SALESFORCE_USERNAME=you@example.com
SALESFORCE_PASSWORD=yourpassword
SALESFORCE_KEY=yoursecuritytoken
SALESFORCE_INSTANCE_URL=https://your-instance.my.salesforce.com
```
