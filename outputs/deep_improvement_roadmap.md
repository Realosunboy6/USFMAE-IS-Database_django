# Deep Improvement Roadmap for USFMAE-IS

Date: 2026-04-30

## Current Position

USFMAE-IS is already a strong class-project prototype. It has a working Django app, normalized database models, seeded demonstration data, dashboards, reports, searchable students, payment records, aid applications, administrator review pages, tests, and a professional visual style.

The next improvement should not be random features. The best direction is to make the system feel like a real student finance portal: clearer student action items, better administrator workflows, filtered reports, and stronger database traceability.

## What A Better Version Should Become

The improved project should be presented as:

> A student finance transparency and aid review database system that helps students understand charges, payments, balances, aid requirements, and application status while helping administrators review records, track missing documents, and generate decision-ready reports.

That is stronger than saying it is only a Django version of an Access database.

## Recommended Improvements

### 1. Add Student Action Items

Priority: Highest

Why it matters:

University financial aid portals commonly show students required actions such as missing documents, incomplete applications, unresolved balances, or pending review items. This makes the app feel more realistic and directly solves the student confusion problem.

What to add:

- `ActionItem` model
- student foreign key
- title
- description
- category such as balance, document, payment, aid, or general
- due date
- status such as open, completed, waived
- priority such as low, normal, urgent

Pages to add:

- student action item list
- dashboard section showing urgent/open action items
- admin action item management

Why this should come first:

It is easy to explain in a presentation and immediately makes the app more useful.

### 2. Add Document Tracking For Aid Applications

Priority: Highest

Why it matters:

Right now, the app has a single `docs_submitted` boolean. Real aid workflows usually need to track which documents are required, which have been submitted, and which are still missing.

What to add:

- `RequiredDocument` model
- `ApplicationDocument` model
- document name
- document status
- received date
- notes

Examples:

- FAFSA confirmation
- income verification
- enrollment verification
- scholarship essay
- transcript

Why this is better:

It turns the aid application workflow from a simple form into a real review process.

### 3. Add Filtered Reports

Priority: High

Why it matters:

Current reports show useful data, but administrators need filters. A polished database project should support report questions like:

- show students with balances above a threshold
- show overdue charges
- show pending aid applications
- show missing-document applications
- show payments by date range
- show records by semester

What to add:

- report filter forms
- balance threshold filter
- semester filter
- status filter
- date range filter
- overdue-only option

Why this is a strong class-project improvement:

Filtered reports demonstrate that the database is not just storing data; it supports decision-making.

### 4. Add Role-Based Access

Priority: High

Why it matters:

The project has two natural users: Student and Administrator. A stronger system should separate what each user can see.

What to add:

- Django login
- groups for Student and Administrator
- student users linked to student records
- student-only dashboard
- administrator-only reports and review tools

Suggested scope:

Keep it simple. Do not overbuild a full enterprise permission system. Use Django users and groups.

Why this matters:

It makes the system more realistic and protects student financial information.

### 5. Add Audit Trail

Priority: Medium

Why it matters:

Financial records need traceability. If a payment, charge, or aid decision changes, the system should know who changed it and when.

What to add:

- simple `AuditLog` model, or
- use Django admin history for admin changes, or
- add `created_at`, `updated_at`, and `updated_by` fields to important models

Best class-project version:

Add timestamps to key models first:

- StudentCharge
- Payment
- AidApplication

Then show a short “last updated” field in admin/report pages.

### 6. Improve Eligibility Review

Priority: Medium

Why it matters:

Current eligibility checks GPA, enrollment status, and documents. That is clear, but it can be made stronger without becoming too complex.

What to add:

- eligibility explanation text
- show each rule separately
- pass/fail for GPA
- pass/fail for enrollment
- pass/fail for documents
- final recommendation: eligible, not eligible, needs review

Why this helps:

Administrators and students can see why an application is or is not eligible.

### 7. Add Overdue Balance Logic

Priority: Medium

Why it matters:

Student finance systems often care about deadlines and past-due balances.

What to add:

- computed overdue status on charges
- report for students with overdue charges
- dashboard metric for overdue total
- badge for overdue, due soon, or paid

Why this helps:

It makes the database support early intervention before balances become bigger problems.

### 8. Improve Demo Data

Priority: Medium

Why it matters:

The current sample names are now distinct, which is good. The next step is making the financial data look more realistic.

What to add:

- more scholarships
- more fee categories
- mixed payment methods
- varied due dates
- varied application statuses
- some overdue balances
- some completed aid applications

Suggested sample scale:

- 100 students
- 6 fee categories
- 5 scholarships
- 150-200 charges
- 80-120 payments
- 50-70 aid applications
- 50-100 action items

### 9. Add Export Buttons

Priority: Low

Why it matters:

Administrators often need reports outside the system.

What to add:

- export balance report to CSV
- export payment report to CSV
- export aid status report to CSV

Why low priority:

It is useful, but filtered reports and document tracking matter more first.

### 10. Improve README With Screenshots Later

Priority: Low

Why it matters:

The README now correctly focuses on the database. Later, screenshots would make GitHub look better.

What to add:

- dashboard screenshot
- student profile screenshot
- reports screenshot
- short “database problem solved” paragraph

## Best Implementation Order

### Phase 1: Make The System More Real

1. Add Student Action Items.
2. Add Document Tracking.
3. Improve demo data around missing documents, overdue balances, and mixed statuses.

This phase makes the project feel like a real student finance system.

### Phase 2: Make It More Useful For Administrators

1. Add filtered reports.
2. Add overdue balance logic.
3. Add eligibility explanation.

This phase makes the database support real decisions.

### Phase 3: Make It More Professional

1. Add role-based access.
2. Add audit timestamps.
3. Add CSV exports.
4. Add screenshots to README.

This phase makes it look more complete and production-minded.

## Recommended Next Build

The best next build is:

> Add Action Items and Document Tracking.

Why:

- It matches real student finance portals.
- It strengthens the database design.
- It gives the dashboard more meaningful content.
- It makes aid applications more realistic.
- It is still manageable for a class project.

## Proposed New Tables

### ActionItem

Fields:

- action item ID
- student
- title
- description
- category
- priority
- due date
- status
- created date

### RequiredDocument

Fields:

- document ID
- document name
- description
- applies to award type
- active status

### ApplicationDocument

Fields:

- application
- required document
- status
- received date
- notes

## Final Decision

We should improve USFMAE-IS by adding:

1. Student Action Items
2. Aid Document Tracking
3. Filtered Reports
4. Overdue Balance Logic
5. Eligibility Explanation

Start with the first two. They will make the project look much more real without making the code too complicated.

## Sources Consulted

- University student financial services portal examples showing balance, payment history, financial aid status, action items, and authorized access patterns.
- University financial aid portal examples showing document tracking, To-Do lists, award status, and required action notifications.
- Django role-based access control guidance using built-in users, groups, and permissions.
- Django audit logging guidance around model change tracking and admin history.
