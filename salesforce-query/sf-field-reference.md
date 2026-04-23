# Salesforce schema reference — Meeting Prep Agent

A clean list of every object, field, and picklist value captured so far. Everything here was confirmed from Object Manager / field detail pages. Fields not listed here still need verification.

---

## Custom objects (API names)

| Object label | API name |
|---|---|
| Fiscal Year Record | `Fiscal_Year_Record__c` |
| Partner Engagement | `Partner_Engagement__c` |
| Partner Engagement Attendee | `Partner_Engagement_Attendee__c` |
| Stakeholder | `Stakeholder__c` |
| Competitor Detail | `Competitor_Detail__c` |
| Onboarding Record | `Onboarding_Record__c` |

### Gong managed-package objects

| Object label | API name |
|---|---|
| Gong Related Accounts (junction) | `Gong__Related_Account__c` |
| Gong Related Contacts | `Gong__Related_Contact__c` |
| Gong Related Leads | `Gong__Related_Lead__c` |
| Gong Related Opportunities | `Gong__Related_Opportunity__c` |
| Gong Scorecard | `Gong__Gong_Scorecard__c` |
| Conversation (the actual call record) | `Gong__Gong_Call__c` |

---

## Account (standard object — custom fields)

| Field | API name | Notes |
|---|---|---|
| DPM | `Account_Manager__c` | Lookup to User |
| OM | `Onboarding_Manager__c` | Lookup to User |
| TIS | `ZD_TIS_Assigned__c` | Lookup to User |
| Partnership Status | `Partnership_Status__c` | |
| Teachers | `Number_of_Teachers__c` | Two teacher fields exist; semantics to confirm |
| Teachers (alternate) | `Total_Teachers__c` | |
| 2025-2026 Segment | `X2025_2026_Segment__c` | Picklist — values below |

**No ARR field.** Use `Opportunity.Contract_Term__c` (years) + teacher counts + Segment as the size proxy.

### `X2025_2026_Segment__c` picklist values

- Jumbo
- Extra Large
- Large
- Medium
- Small
- Field
- Mid Market

---

## `Fiscal_Year_Record__c`

| Field | API name | Type |
|---|---|---|
| Account | `Account__c` | Master-Detail to Account |
| Name | `Name` | Text — holds "2025-2026" style values |
| Partnership Health Score | `Partnership_Health_Score__c` | Picklist |
| Partnership Health Score Details | `Partnership_Health_Score_Details__c` | Text Area |
| Renewal Status | `Renewal_Status__c` | Picklist |
| Forecasted Renewal Date | `Forecasted_Renewal_Date__c` | Date |
| Use Case | `Use_Case__c` | |
| Has Superintendent | `Has_Superintendent__c` | Checkbox |
| SMS | `SMS__c` | Feature Adoption picklist |
| Robocalls | `Robocalls__c` | Feature Adoption picklist |
| Attendance | `Attendance__c` | Feature Adoption picklist |
| Teacher↔Student Messaging | `T_S_Messaging__c` | Feature Adoption picklist |
| 1-Way Announcements | `District_1_Way_Announcements__c` | Feature Adoption picklist |
| Self-Serve Message Access | `Self_Serve_Message_Access__c` | Feature Adoption picklist |
| Gong Call (direct link) | `Gong_Call__c` | |
| Gong Recording URL | `Gong_Recording_URL__c` | URL |

### `Partnership_Health_Score__c` picklist values

- Champion
- Healthy
- Lukewarm
- At Risk
- Unclear

### `Renewal_Status__c` picklist values

- Unknown
- Renewal Likely
- Renewal at Risk
- Verbal Commit
- MSA Out for Signature
- MSA Signed - With Order Form
- MSA Signed - Without Order Form

### Feature Adoption picklist values (shared by all six fields)

Applies to `SMS__c`, `Robocalls__c`, `Attendance__c`, `T_S_Messaging__c`, `District_1_Way_Announcements__c`, `Self_Serve_Message_Access__c`:

- Not Discussed
- Discussed - Unclear Intent to Use
- Discussed - Not Intending to Use
- Intends to use - Primary tool
- Intends to use - Non-primary backup tool

---

## `Partner_Engagement__c`

| Field | API name | Type |
|---|---|---|
| Fiscal Year Record | `Fiscal_Year_Record__c` | Master-Detail to FY |
| Engagement Date | `Engagement_Date__c` | Date |
| Key Takeaways / Next Steps | `Key_Takeaways_Next_Steps__c` | Long Text |
| Number of Attendees | `Number_of_Attendees__c` | Number |
| Gong Call (direct link) | `Gong_Call__c` | |
| Gong Recording URL | `Gong_Recording_URL__c` | URL |

Attendee detail lives on `Partner_Engagement_Attendee__c` (fields TBD).

---

## `Onboarding_Record__c`

| Field | API name | Type |
|---|---|---|
| Account | `Account__c` | Lookup / Master-Detail |
| Rostering Intent | `Rostering_Intent__c` | Picklist (values TBD) |

---

## Opportunity (standard object — custom fields)

| Field | API name | Notes |
|---|---|---|
| Contract Term (years) | `Contract_Term__c` | |
| Is Opp Head-to-Head | `Is_Opp_Head_to_Head__c` | Checkbox |
| Primary Competitor | `Head_to_Head_Competitor__c` | |
| Secondary Competitor | `Head_to_Head_Competitor_Secondary__c` | |
| Primary Motivation | `Primary_Motivation__c` | |
| Additional Motivations | `Additional_Motivations__c` | |
| Motivation Notes | `Motivation_Notes__c` | Long Text |
| Demo Meeting Notes | `Demo_Meeting_Notes__c` | Long Text |
| Key Risks / Opportunities | `Key_Risks_Opportunities__c` | Long Text |
| Win Reasons (if closed-won) | `Win_Reasons__c` | |
| Key features that won the district | `What_key_features_won_over_the_district__c` | |
| Departments engaged | `What_departments_did_we_engage_with__c` | |
| Why we didn't win outright | `Why_didn_t_we_win_outright__c` | |
| What would put us at risk of losing them | `What_would_put_us_at_risk_of_losing_them__c` | |

---

## `Gong__Related_Account__c` (junction)

Links a `Gong__Gong_Call__c` (Conversation) to an Account.

| Field | API name | Type |
|---|---|---|
| ID | `Name` | Auto Number, format `GA-{00000}` |
| Account (matching key) | `Gong__Related_Entity_ID__c` | **Lookup(Account)** |
| Account Name (display) | `Gong__Account_Name__c` | Formula(Text) |
| Primary Account flag | `Gong__Primary_Account__c` | Checkbox |
| Conversation link | `Gong__Gong_Interaction__c` | Master-Detail to `Gong__Gong_Call__c` |
| Participants Emails | `Gong__Participants_Emails__c` | Text |
| Duration | `Gong__Duration__c` | Number |
| Last Modified By | `LastModifiedById` | |
| Created By | `CreatedById` | |

---

## `Gong__Gong_Call__c` (the Conversation object — actual call record)

| Field | API name | Notes |
|---|---|---|
| Name | `Name` | Standard Name field |
| Gong Call ID | `Gong__Call_ID__c` | **External Gong ID — this is what you pass to Gong's API** |
| Call Date/Time | `Gong__Scheduled__c` | DateTime |
| Call Title | `Gong__Title__c` | |
| AI Call Brief | `Gong__Call_Brief__c` | Gong's AI summary — already synced into SF |
| Call URL | `Gong__View_Call__c` | URL to Gong UI |
| Duration | `Gong__Call_Duration__c` | |
| Direction | `Gong__Direction__c` | |

---

## Still to verify (open in Object Manager when you get a minute)

- `Stakeholder__c` — all fields
- `Partner_Engagement_Attendee__c` — all fields (specifically: the Contact reference, decision-maker flag, and role)
- `Competitor_Detail__c` — all fields
- `Fiscal_Year_Record__c` — full list of `Has_*__c` checkboxes (we have `Has_Superintendent__c` only)
- `Onboarding_Record__c` — `Rostering_Intent__c` picklist values
- Semantic difference between `Account.Number_of_Teachers__c` and `Account.Total_Teachers__c`

---

## Example traversal paths

**Account → Gong calls (last 90 days):**

```
Account.Id
  ↓ = Gong__Related_Account__c.Gong__Related_Entity_ID__c
  ↓ Gong__Gong_Interaction__c (Master-Detail)
Gong__Gong_Call__c (Title, Scheduled, Call_Brief, View_Call, Call_ID)
```

**Account → Partner Engagement narrative:**

```
Account.Id
  ↓ = Fiscal_Year_Record__c.Account__c
  ↓ Partner_Engagement__c.Fiscal_Year_Record__c (Master-Detail)
Partner_Engagement__c.Key_Takeaways_Next_Steps__c
```

**Account → Rostering Intent:**

```
Account.Id
  ↓ = Onboarding_Record__c.Account__c
Onboarding_Record__c.Rostering_Intent__c
```
