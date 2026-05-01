# USFMAE-IS School-Readiness Assessment

Date: 2026-05-01

## Bottom Line

USFMAE-IS is a strong class-project prototype, but it is not yet ready for real school use. The current system proves the idea: students can see balances, payments, aid applications, documents, action items, and hold-risk signals. To become something a school could depend on, the project needs production-grade privacy, security, auditing, integrations, reliability, and administrator workflow controls.

The right product direction is:

> A student finance transparency and aid workflow platform that helps schools reduce student confusion around balances, missing aid documents, payment status, and registration-risk actions.

## What Is Already Strong

- Clear domain model for students, charges, payments, scholarships, applications, administrators, required documents, and action items.
- Student-private profile route at `/my-profile/`.
- Staff-only administrative pages using Django authentication.
- Searchable student list and reports.
- Demo data seeding with many sample students.
- CSV import command for Access-style exports.
- Automated Django tests currently pass.
- Basic hold-risk logic already exists.

## Major Gaps Before School Use

### 1. Security And Privacy

The app currently uses development settings:

- hardcoded `SECRET_KEY`
- `DEBUG = True`
- SQLite database
- local-only `ALLOWED_HOSTS`
- no MFA
- no password reset or institutional identity provider
- no field-level audit trail
- no formal data retention policy

For real schools, student financial records must be treated as sensitive education records. The U.S. Department of Education says education records are records directly related to a student and maintained by a school or by a party acting for the school; it explicitly includes student financial information at the postsecondary level.

Minimum upgrades:

- environment-based secrets
- `DEBUG = False` in deployed environments
- PostgreSQL
- HTTPS-only cookies
- CSRF/session hardening
- role-based authorization beyond simple `is_staff`
- MFA for staff
- audit logging for sensitive reads and writes
- encrypted backups
- documented retention and deletion rules

### 2. FERPA-Oriented Access Controls

FERPA does not mean every school employee can see every record. Department of Education guidance says access without consent is limited to school officials with legitimate educational interests.

The app needs roles such as:

- Student
- Student Accounts Staff
- Financial Aid Reviewer
- Supervisor
- Auditor / Read-only Compliance
- System Administrator

Each role should have explicit permissions. For example:

- students can read only their own profile
- aid reviewers can update aid documents and application decisions
- billing staff can manage charges and payments
- auditors can view logs but not edit records
- system administrators can manage users but should not automatically have broad student-record business access

### 3. Audit Trail

Real schools need to know who viewed or changed sensitive records, when, and why.

Add an `AuditLog` model or equivalent event table with:

- actor user
- affected student
- action type
- object type and object id
- before/after summary for writes
- timestamp
- IP address / user agent where appropriate
- reason or workflow context for high-risk actions

FERPA guidance also says schools generally must maintain records of requests for access to, and disclosures of, personally identifiable information from education records, subject to listed exceptions.

### 4. Workflow Maturity

The app currently tracks documents and action items, which is good. It needs workflow controls:

- assigned owner for each action item
- due dates and escalation
- comments/history on applications
- document upload support with secure storage
- document review status history
- application decision reasons
- notification queue
- student messages that are plain-language and actionable
- staff dashboard filtered by assigned workload

The existing `docs_submitted` boolean should eventually become derived from the detailed `ApplicationDocument` statuses, not separately maintained by hand.

### 5. School System Integrations

Schools will not want to re-enter all data manually. The product needs integration boundaries:

- SIS import/export for student identity, enrollment, program, term
- bursar/accounting import for charges, payments, balances
- financial aid system import for awards, FAFSA/ISIR status, verification requirements
- SSO with SAML/OIDC
- optional payment processor integration
- CSV import is useful, but should become a managed import pipeline with validation, previews, mapping, and rollback

### 6. Data Model Expansion

For real use, add:

- School / tenant model
- Academic term model
- Student account ledger model
- Charge/payment allocation model
- Aid award model separate from aid application
- Payment plan and installment models
- Document upload metadata
- Notification model
- User role/permission models
- Audit and disclosure logs

The current `StudentCharge` plus `Payment` totals are fine for a demo, but real balances usually need a ledger so the system can answer exactly what charge a payment satisfied.

### 7. Operations And Reliability

A school-usable app needs:

- deployment pipeline
- error monitoring
- structured logs
- database backups and restore testing
- uptime monitoring
- migration process
- staging environment
- load testing
- dependency vulnerability scanning
- documented incident response

If the app handles nonpublic financial information, the FTC Safeguards Rule is relevant for covered financial institutions and requires a written information security program, risk assessments, access controls, encryption, MFA, activity logging, monitoring/testing, training, service-provider oversight, and an incident response plan.

## Recommended Build Phases

### Phase 1: Harden The Current Prototype

- Move secrets and config to environment variables.
- Add production settings.
- Switch local production-like dev to PostgreSQL.
- Remove student-facing links to staff-only pages.
- Make `aid_review` document form either functional or remove it.
- Add tests around student/staff authorization.
- Add created/updated timestamps to financial models.
- Add simple audit logging for writes.

### Phase 2: Make It A Real School Workflow Tool

- Add roles and permissions.
- Add staff workload queues.
- Add document uploads.
- Make document status drive application completeness.
- Add application comments and decision reasons.
- Add notifications for missing documents, due-soon charges, and status changes.
- Add import validation screens.

### Phase 3: Make It Institution-Ready

- Add school/tenant support.
- Add SSO.
- Add complete audit and disclosure logging.
- Add encrypted file storage.
- Add ledger-based accounting.
- Add payment plans.
- Add API endpoints for SIS/billing/aid integrations.
- Add deployment, monitoring, backup, and incident-response documentation.

### Phase 4: Pilot Readiness

- Run a security review.
- Run accessibility review.
- Run data-migration tests against realistic sample exports.
- Run a staff workflow pilot with non-production data.
- Create admin/user documentation.
- Create support procedures.
- Have legal/compliance review FERPA, GLBA/Safeguards, state privacy laws, and school procurement requirements.

## Immediate Code Issues To Fix

- `finance/templates/finance/student_detail.html` shows a staff-only "Manage items" link to students.
- `finance/views.py` creates `document_form` in `aid_review`, but `admin_review.html` does not use it to save application documents.
- `docs_submitted` duplicates document-level status and can drift out of sync.
- `hold_risk_status` is based on aggregate balance plus due dates, but does not allocate payments to charges.
- Production settings do not exist yet.
- No formal audit trail exists.

## External References

- U.S. Department of Education, Protecting Student Privacy FAQ: education records include student financial information at the postsecondary level.
- U.S. Department of Education, FERPA FAQ: employee access is limited to school officials with legitimate educational interests.
- U.S. Department of Education, FERPA FAQ: schools generally must maintain records of requests for access to and disclosures of PII from education records, with exceptions.
- FTC, Safeguards Rule guidance: covered institutions need a written information security program, risk assessment, access controls, encryption, MFA, activity logging, testing, training, service-provider oversight, incident response, and breach notification rules.

## Verdict

This can become useful to schools, but the next step should not be more visual polish. The next step should be trust infrastructure: roles, audit logs, production settings, secure document handling, and workflow history. That is what turns it from a nice demo into something a school could seriously evaluate.
