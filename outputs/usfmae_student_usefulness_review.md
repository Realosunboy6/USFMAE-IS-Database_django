# Peer Review of USFMAE-IS Student Usefulness Plan

Date: 2026-04-30

## Overall Review

The plan is strong because it focuses on practical student problems instead of adding features randomly. The most convincing ideas are student-private profiles, action items, document tracking, and hold-risk warnings. These features directly address real weaknesses in university student finance experiences: students often do not know what is missing, what they owe, or what action to take next.

## Strengths

### Strong Real-World Problem Alignment

The plan correctly identifies the main student pain point: financial information is often technically available but not understandable. Students need a clear next step, not just tables.

### Good Feature Prioritization

The recommendation to build student login, document checklist, and action items first is correct. These features are more valuable than adding extra charts or cosmetic changes.

### Good Database Direction

The plan improves the database by adding meaningful workflow entities:

- users linked to students,
- action items,
- required documents,
- application documents.

These are realistic additions to the current schema.

## Weaknesses

### Payment Plan May Be Too Large For Immediate Scope

Payment plans are useful, but they introduce more complexity than action items and document tracking. If built too early, they could distract from the core aid workflow.

Recommendation:

Keep payment plans as a later feature.

### Aid Status Timeline Needs Careful Scope

A full aid disbursement timeline can become complicated because real aid systems connect to external federal, state, billing, and registrar systems.

Recommendation:

Use a simplified class-project timeline:

- submitted,
- missing documents,
- under review,
- approved,
- denied,
- applied to balance.

Do not claim to model full federal aid processing.

### Role-Based Access Must Stay Simple

Full production-grade access control is not needed. A class project can use Django users and staff flags.

Recommendation:

Use:

- student users,
- staff users,
- `/my-profile/` for students,
- staff-only admin pages.

Avoid overbuilding custom roles unless needed later.

## Improved Recommendation

The best implementation path is:

1. Finish student login/private profile.
2. Make the student profile the main student experience.
3. Show action items at the top of the student profile.
4. Show required aid documents directly under aid applications.
5. Add hold-risk status after balances and due dates.
6. Add filtered admin reports.
7. Add payment plans only after the above features are stable.

## What To Build Next

The next best feature after the current login work is:

### Hold Risk Indicator

Why:

- The app already has charges, payments, balances, and due dates.
- The logic is easy to explain.
- It directly helps students avoid financial blocks.

Suggested labels:

- Clear
- Balance Due
- Due Soon
- Overdue

This can be displayed on:

- student profile,
- dashboard,
- reports.

## Final Verdict

The plan is worth following. It should be implemented in small phases, starting with the features that make student confusion visible and actionable. The app should not try to become a full enterprise financial aid platform. It should become a clear, realistic, student-centered finance and aid tracking system.
