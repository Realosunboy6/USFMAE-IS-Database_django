# Red-Team Review: NIU Adoption Case for USFMAE-IS

Date: 2026-05-01

## Executive Verdict

The current adoption case is promising but still too soft for a real NIU audience. A skeptical NIU reviewer would likely say:

> "This duplicates things MyNIU already does, introduces student-data risk, lacks enterprise security evidence, and is not yet integrated with official systems."

That does not kill the idea. It means the positioning must be narrower:

> USFMAE-IS is not a replacement for MyNIU. It is a student finance clarity and early-intervention dashboard that can pilot with de-identified or exported data to improve student understanding of balances, aid blockers, holds, and next actions.

## Strongest Objections NIU Could Raise

### 1. "MyNIU Already Does This"

NIU already has Financial Account, Tasks/To-Do List, statements, payments, pending aid, holds, shared access, and PeopleSoft governance.

Risk:

- The project looks duplicative.
- Offices may not want another system.
- PeopleSoft teams may reject anything that creates parallel records.

Fix:

- Do not pitch replacement.
- Pitch "clarity layer" and "student intervention dashboard."
- Use official systems as source of truth.
- Start read-only/import-only.
- Show side-by-side examples where MyNIU gives data but USFMAE-IS gives plain-language action.

### 2. "This Could Mislead Students"

If USFMAE-IS shows a balance, hold risk, or aid status that differs from MyNIU, students could make bad payment or registration decisions.

Risk:

- Incorrect guidance could cause financial harm.
- Staff may distrust the tool.
- Legal/compliance stakeholders may block it.

Fix:

- Label data freshness clearly.
- Show source system and last import time.
- Avoid "official balance" language unless reconciled.
- Add "View official record in MyNIU" links if allowed.
- Keep first pilot limited to explanations and alerts, not final decisions.

### 3. "Security Evidence Is Missing"

A Django prototype with SQLite, hardcoded development settings, no MFA, no audit trail, and no deployment controls will not pass a serious security review.

Risk:

- Immediate denial by DoIT or security review.

Fix:

- Add production settings.
- Move secrets to environment variables.
- Use PostgreSQL.
- Add role-based access control.
- Add audit logs.
- Add staff MFA through SSO/OIDC.
- Add encryption-at-rest plan.
- Add backup/restore plan.
- Prepare a security architecture document.

### 4. "FERPA Access Rules Are Too Weak"

The current app uses `is_staff`, which is too broad for real student financial data.

Risk:

- Any staff user could see too much.
- No legitimate-interest boundary.
- No office-specific permission model.

Fix:

- Add roles: Student, Bursar Staff, Financial Aid Reviewer, Advisor, Supervisor, Auditor, System Admin.
- Limit data by role.
- Add reason-for-access for sensitive lookups.
- Log all staff student-record views.
- Add periodic access review.

### 5. "Accessibility Could Block Procurement"

NIU requires accessible technology and VPAT/WCAG documentation. The current UI has not been tested.

Risk:

- Procurement/accessibility review blocks adoption.
- Student-facing system fails WCAG expectations.

Fix:

- Run automated accessibility checks.
- Add keyboard-only acceptance tests.
- Fix focus states, table semantics, form errors, contrast, headings.
- Produce a draft VPAT/ACR.
- Prefer HTML reports over PDFs.

### 6. "No Integration Plan"

Without a real data integration path, the tool is only a duplicate database.

Risk:

- Manual data entry is unacceptable.
- CSV imports may be seen as fragile.
- PeopleSoft integration may be expensive.

Fix:

- Phase 1: de-identified demo data.
- Phase 2: read-only CSV export/import pilot.
- Phase 3: approved API or scheduled secure file transfer.
- Phase 4: writeback only if campus governance approves.

### 7. "Who Owns The Workflow?"

Action items and document statuses can cross Bursar, Financial Aid, Advising, and Records.

Risk:

- No office wants to own another queue.
- Conflicting advice across offices.
- Action items become stale.

Fix:

- Add action owner office.
- Add escalation date.
- Add status history.
- Add stale-action report.
- Add contact routing by issue category.
- Pilot with one office first, not all offices at once.

### 8. "The Current Accounting Logic Is Too Simple"

The app calculates balance as total charges minus total payments. Real accounts need term, due date, aid credits, refunds, reversals, payment allocations, late fees, holds, and payment plans.

Risk:

- Incorrect balance/risk calculation.

Fix:

- Rename current balance to "estimated imported balance" unless official.
- Add ledger model later.
- Keep hold-risk logic explanatory, not authoritative.
- Base official risk on imported official hold/balance fields if available.

### 9. "No Evidence Students Need This"

The idea seems useful, but adoption needs proof.

Risk:

- Decision-makers may see it as a student project, not a campus need.

Fix:

- Run usability interviews with students.
- Measure whether students can answer: amount owed, pending aid, missing docs, next step.
- Compare MyNIU-only vs USFMAE-IS explanation.
- Collect task-completion time and error rate.
- Use de-identified screenshots.

### 10. "Support Burden Is Undefined"

If students use it, someone must answer questions when data looks wrong.

Risk:

- Bursar and Financial Aid offices inherit more tickets.

Fix:

- Add issue category routing.
- Add "data last updated" context.
- Add "contact this office" guidance.
- Add admin-facing explanation of how each alert was generated.

## Red-Team Scorecard

| Area | Current State | NIU-Ready Bar | Risk |
|---|---|---|---|
| Product positioning | Too broad | Clarity layer, not replacement | High |
| Security | Prototype | Reviewed, documented, hardened | Critical |
| FERPA access | `is_staff` | Role/need-based access | Critical |
| Accessibility | Untested | WCAG 2.1 AA + VPAT/ACR | High |
| Integration | Manual/demo import | Read-only official data path | High |
| Accuracy | Demo calculations | Official-source reconciliation | High |
| Workflow ownership | Generic | Office-owned queues | Medium |
| Evidence | Assumed usefulness | Student/staff pilot data | Medium |
| Procurement packet | Missing | Security, accessibility, support docs | High |

## Revised Adoption Pitch

Use this:

> USFMAE-IS is a student finance clarity dashboard designed to reduce confusion around balances, pending aid, missing documents, and registration-risk actions. It does not replace MyNIU or PeopleSoft. It imports or reads approved data, explains it in plain language, and gives students and staff actionable next steps. The first pilot can run with de-identified or read-only exported data.

Avoid this:

> USFMAE-IS is a school financial system that can replace existing student account and aid tools.

## Minimum Viable NIU Pilot

### Scope

- One term.
- De-identified or limited student sample.
- Read-only data.
- No payment processing.
- No official decisioning.
- One office owner, preferably Bursar or Financial Aid.

### Features

- Student clarity dashboard.
- Missing document checklist.
- Imported balance/charge/payment summary.
- Hold-risk explanation.
- Next-action list.
- Staff queue for students with missing documents or high-risk balances.
- Exportable pilot metrics.

### Controls

- Role-based access.
- Audit log.
- Last-import timestamp.
- No writeback.
- Accessibility test report.
- Security review packet.

### Success Metrics

- Students identify next step faster.
- Fewer wrong-office questions.
- Staff can identify high-risk students faster.
- Students understand whether pending aid is included.
- Students understand what document is blocking aid.

## Code-Level Next Sprint

1. Add roles and permissions beyond `is_staff`.
2. Add `AuditLog` for staff views and all financial/aid writes.
3. Add `updated_at`, `created_by`, and `updated_by` where needed.
4. Hide staff-only links from student profile.
5. Make document checklist authoritative and remove duplicated `docs_submitted` logic over time.
6. Add source-system metadata: source name, imported at, import batch.
7. Add import validation preview.
8. Add accessibility-focused template improvements.
9. Add production settings file.
10. Add tests for role access, audit logging, and student data isolation.

## Final Red-Team Judgment

The project is adoptable only if it becomes more honest and narrower. The strongest form is not "a new school finance database." It is:

> a secure, accessible, read-only student finance clarity dashboard that helps NIU reduce confusion and intervene earlier, while MyNIU/PeopleSoft remain the official systems.

That pitch has a chance. The replacement-system pitch does not.
