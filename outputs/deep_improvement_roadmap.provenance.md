# Provenance: Deep Improvement Roadmap

Date: 2026-04-30

## Local Project Files Reviewed

- `finance/models.py`
- `finance/views.py`
- `finance/forms.py`
- `finance/services.py`
- `README.md`
- `finance/templates/finance/*.html`

## Local Findings

### Current Strengths

- Models cover the core database entities:
  - Student
  - FeeCategory
  - StudentCharge
  - Payment
  - Scholarship
  - AidApplication
  - Administrator
- Views cover the main workflows:
  - dashboard
  - student list and detail
  - charges
  - payments
  - aid applications
  - aid review
  - reports
- The app has tests and demo data.
- The README now focuses on the database purpose and schema.

### Current Gaps

- No student action item model.
- Aid document tracking is only a boolean field.
- Reports are not filterable.
- No role-based login separation between students and administrators.
- No explicit audit trail or timestamps on financial changes.
- Eligibility result does not explain which rule passed or failed.

## External Sources Consulted

### Student Finance Portal Feature Benchmark

Search topic:

`student financial services portal features balance payment history financial aid status university`

Used for:

- balance and payment information,
- payment history,
- aid status,
- billing statements,
- action items,
- authorized/proxy access,
- direct deposit and payment plan ideas.

### Financial Aid Portal Feature Benchmark

Search topic:

`student financial aid application tracking document status university portal features`

Used for:

- document status tracking,
- financial aid To-Do lists,
- processing timelines,
- required action notifications,
- award information pages.

### Django Audit Logging

Search topic:

`Django audit log model changes admin action history best practices`

Used for:

- audit trail concepts,
- admin history,
- timestamp and model change tracking ideas,
- why financial records benefit from traceability.

### Django Role-Based Access Control

Search topic:

`Django class project role based access control student administrator views`

Used for:

- Django users, groups, and permissions,
- student/admin role separation,
- least-privilege access for sensitive records.

## Decision Rationale

The highest-value next features were chosen because they:

1. Match real university finance and aid portals.
2. Improve the database design, not just the visual interface.
3. Are easy to explain in a class presentation.
4. Make the dashboard and reports more meaningful.
5. Keep the project manageable.

## Recommended Next Implementation

Start with:

- `ActionItem`
- `RequiredDocument`
- `ApplicationDocument`

Then add:

- filtered reports,
- overdue balance logic,
- eligibility explanations,
- role-based access,
- audit timestamps,
- CSV exports.

## Limitations

- This roadmap is based on source review and web benchmarking, not a direct interview with university staff.
- The project remains a class prototype, so recommendations avoid enterprise-level financial aid complexity.
- Some improvements, such as full role-based access, require more implementation and testing than simple display changes.
