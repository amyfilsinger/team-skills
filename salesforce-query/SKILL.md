---
name: salesforce-query
description: Answer natural-language questions about ClassDojo's Salesforce data by translating them to SOQL and hitting the Salesforce REST API. Use whenever the user asks questions like "how many active partners do we have", "which districts are at risk of renewal", "pipeline for this quarter", "list jumbo accounts", "what's the health-score breakdown", "which districts have the highest teacher counts", or any question that would live in Salesforce reports/dashboards. Triggers on mentions of Salesforce, SFDC, partners, partnership status, renewals, fiscal year records, partner engagements, opportunities, pipeline, Gong calls tied to accounts, or feature adoption (SMS, Robocalls, Attendance, T↔S Messaging, 1-Way Announcements).
---

# Salesforce Query

Turn natural-language questions about ClassDojo's Salesforce data into SOQL, execute against the REST API, and return answers.

## Schema reference — READ THIS FIRST

Every query should use field names from [`sf-field-reference.md`](sf-field-reference.md) in this skill folder. Do not guess field names. If a field you need isn't in the reference, either:
1. Run a `describe` call on the object and pick the right field, or
2. Ask the user and update the reference file afterward so the next query is faster.

### Most-used mappings

| Business concept | Object / Field |
|---|---|
| Active partner account | `Account` where `Partnership_Status__c = 'Active'` (verify the literal value with the user; if unknown run a `GROUP BY Partnership_Status__c` first) |
| District size segment | `Account.X2025_2026_Segment__c` — values: Jumbo, Extra Large, Large, Medium, Small, Field, Mid Market |
| DPM / OM / TIS owner | `Account.Account_Manager__c` / `Onboarding_Manager__c` / `ZD_TIS_Assigned__c` (all Lookup to User) |
| Teacher count | `Account.Number_of_Teachers__c` or `Total_Teachers__c` (semantics unconfirmed — ask if precision matters) |
| Renewal status | `Fiscal_Year_Record__c.Renewal_Status__c` — values: Unknown, Renewal Likely, Renewal at Risk, Verbal Commit, MSA Out for Signature, MSA Signed - With Order Form, MSA Signed - Without Order Form |
| Partnership health score | `Fiscal_Year_Record__c.Partnership_Health_Score__c` — values: Champion, Healthy, Lukewarm, At Risk, Unclear |
| Forecasted renewal date | `Fiscal_Year_Record__c.Forecasted_Renewal_Date__c` |
| Feature adoption (SMS / Robocalls / Attendance / T↔S / 1-Way / Self-Serve) | All live on `Fiscal_Year_Record__c` — `SMS__c`, `Robocalls__c`, `Attendance__c`, `T_S_Messaging__c`, `District_1_Way_Announcements__c`, `Self_Serve_Message_Access__c`. Shared picklist: Not Discussed / Discussed - Unclear / Discussed - Not Intending / Intends to use - Primary / Intends to use - Non-primary backup |
| Pipeline / deals | `Opportunity` (standard object) — contract length in `Contract_Term__c` (years); **no ARR field** — use Contract Term + teacher count + Segment as size proxy |
| Competitive / win-loss | `Opportunity.Is_Opp_Head_to_Head__c`, `Head_to_Head_Competitor__c`, `Win_Reasons__c`, `Why_didn_t_we_win_outright__c` |
| Partner engagement notes | `Partner_Engagement__c.Key_Takeaways_Next_Steps__c` (linked via `Fiscal_Year_Record__c`) |
| Gong call on an account | `Gong__Related_Account__c.Gong__Related_Entity_ID__c` → `Gong__Gong_Interaction__c` → `Gong__Gong_Call__c` |

For relationship traversal examples see the "Example traversal paths" section at the bottom of the reference file.

## Credentials

From `/Users/amyfilsingerwork/Desktop/Cowork Ouput/.env`:

- `Salesforce_Key` — treat as a bearer access token unless proven otherwise.
- `SALESFORCE_INSTANCE_URL` — org base URL (e.g. `https://classdojo.my.salesforce.com`). If missing, ask the user to add before the first query.

**Never print the key.** Load via:

```bash
set -a; source "/Users/amyfilsingerwork/Desktop/Cowork Ouput/.env"; set +a
```

If the first call returns `401 INVALID_SESSION_ID`, the key isn't a bearer token — stop and tell the user so they can provide the right credential shape (Connected App client_id/secret, refresh token, etc).

## Workflow

### Step 1 — Map the question to the schema

Before writing SOQL, identify which object(s) the question lives on. Multi-object questions usually go through `Fiscal_Year_Record__c` (renewals, health, feature adoption) back up to `Account`, or through `Opportunity` for deal-state questions.

When the user's phrasing is ambiguous ("active" — active partner? active opportunity? active FY record?), pick the most likely meaning, note it in your answer, and offer to re-run if wrong. Don't block on clarification for routine questions.

### Step 2 — Build the SOQL

Standard aggregate pattern (counting):

```bash
set -a; source "/Users/amyfilsingerwork/Desktop/Cowork Ouput/.env"; set +a
API_VERSION="v60.0"
SOQL="SELECT COUNT() FROM Account WHERE Partnership_Status__c = 'Active'"

curl -s -G \
  -H "Authorization: Bearer ${Salesforce_Key}" \
  -H "Accept: application/json" \
  --data-urlencode "q=${SOQL}" \
  "${SALESFORCE_INSTANCE_URL}/services/data/${API_VERSION}/query"
```

List pattern with join:

```sql
SELECT Account__r.Name, Partnership_Health_Score__c, Renewal_Status__c, Forecasted_Renewal_Date__c
FROM Fiscal_Year_Record__c
WHERE Name = '2025-2026' AND Partnership_Health_Score__c IN ('At Risk','Lukewarm')
ORDER BY Forecasted_Renewal_Date__c ASC
LIMIT 50
```

Discovery pattern (when a picklist value is unknown):

```sql
SELECT Partnership_Status__c, COUNT(Id) FROM Account GROUP BY Partnership_Status__c
```

### Step 3 — Present the answer

- **Counts** → one sentence with the number. Add a bullet breakdown only if it's clearly useful.
- **Lists** → markdown table, key columns only, cap at 25 rows (say so and offer to widen).
- **Always append the SOQL** in a collapsed detail block so the user can sanity-check the mapping:

```markdown
<details><summary>SOQL</summary>

```sql
SELECT COUNT() FROM Account WHERE Partnership_Status__c = 'Active'
```

</details>
```

### Step 4 — Iterate

On follow-ups ("break that down by segment", "only jumbos"), edit the prior SOQL — don't restart. Keep the last query in context.

## Guardrails

- **Read-only.** Never `PATCH`, `POST`, or `DELETE` against Salesforce. If the user asks to modify data, stop and confirm — it's a different skill.
- **No PII dumps.** If a query would return >500 rows of personal data (names, emails, phones), ask before running.
- **Redact keys.** If an API error echoes the token back, scrub it before showing the user.
- **Respect API limits.** Prefer one wide SOQL over several narrow ones; aggregate server-side with `COUNT()` / `GROUP BY` rather than pulling all rows and counting locally.

## Example invocations

**"How many active partners do we have right now?"**
→ `SELECT COUNT() FROM Account WHERE Partnership_Status__c = 'Active'`. If the literal "Active" isn't the right value, the count will be 0 — in which case pivot to the discovery pattern above.

**"Which districts are at risk for 25-26 renewal?"**
→ `SELECT Account__r.Name, Forecasted_Renewal_Date__c, Partnership_Health_Score__c FROM Fiscal_Year_Record__c WHERE Name = '2025-2026' AND Renewal_Status__c = 'Renewal at Risk' ORDER BY Forecasted_Renewal_Date__c`

**"How many jumbo accounts intend to use SMS as primary?"**
→ `SELECT COUNT() FROM Fiscal_Year_Record__c WHERE Account__r.X2025_2026_Segment__c = 'Jumbo' AND SMS__c = 'Intends to use - Primary tool' AND Name = '2025-2026'`

**"Pull the last Partner Engagement takeaway for Memphis."**
→ `SELECT Engagement_Date__c, Key_Takeaways_Next_Steps__c FROM Partner_Engagement__c WHERE Fiscal_Year_Record__r.Account__r.Name LIKE '%Memphis%' ORDER BY Engagement_Date__c DESC LIMIT 1`
