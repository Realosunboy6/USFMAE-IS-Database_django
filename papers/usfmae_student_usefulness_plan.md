# Making USFMAE-IS More Useful for Students

Date: 2026-04-30

## Executive Summary

USFMAE-IS can become much more useful if it is designed around the real confusion students face in university finance systems: unclear balances, missing aid documents, financial aid that appears approved but is not disbursed, account holds, and uncertainty about what action to take next.

The app should focus on becoming a **student finance clarity portal**. Its goal should be simple:

> Every student should be able to log in and immediately understand what they owe, what has been paid, what aid is pending, what documents are missing, and what action they need to complete next.

The strongest improvement path is to build around five student problems:

1. Missing-document delays.
2. Confusing aid application status.
3. Unclear balances and payment history.
4. Registration or account hold risk.
5. No clear next step for the student.

## Real Loopholes The Application Can Cover

### 1. Missing Documents Delay Financial Aid

Many universities use student portals to show financial aid To-Do items and missing document requirements. Verification pages from universities such as Colorado Boulder, Boise State, Florida State, Florida Atlantic, and USF show that missing documents commonly block aid processing. Required items can include verification worksheets, tax transcripts, W2 forms, non-filer letters, and identification documents.

USFMAE-IS can cover this loophole by making missing documents visible and specific. Instead of showing only “documents submitted: yes/no,” the app should show:

- exactly which document is required,
- whether it is missing, submitted, accepted, rejected, or waived,
- when it was received,
- what note the administrator added,
- what deadline the student should follow.

This helps students avoid the common problem of thinking their aid application is complete when one required document is still blocking review.

### 2. Aid Can Look Approved But Still Not Be Ready

Student portals often show multiple stages: application received, document review, award offered, aid accepted, aid disbursed, and aid applied to the bill. A major student pain point is that aid may appear available in one part of a system but not yet applied to the billing ledger.

USFMAE-IS should separate aid status into clearer stages:

- Application submitted
- Missing documents
- Under review
- Eligible
- Approved
- Award posted
- Applied to balance
- Denied

This would make the app more realistic because students often need to know not just whether aid exists, but whether it has actually reduced what they owe.

### 3. Students Need A “What Do I Need To Do?” View

Financial aid portals commonly use To-Do lists, action items, and notification banners. These are important because students may not understand database records or report tables. They need plain-language tasks.

USFMAE-IS can make itself more useful by showing a student action list:

- Submit FAFSA confirmation.
- Upload income verification.
- Review spring balance.
- Make payment or set up payment plan.
- Contact financial aid office.
- Confirm enrollment status.

Each action item should include:

- priority,
- due date,
- category,
- status,
- plain-language description.

This is one of the best improvements because it translates database information into student action.

### 4. Holds And Balances Can Block Progress

Research and policy discussions on institutional holds show that unpaid balances can stop registration, delay graduation, or block transcript access. Inside Higher Ed reported survey evidence that one in five students had been unable to register due to an institutional hold, with higher rates for Black and Latino students. Other reports have discussed transcript holds, stranded credits, and balances that prevent students from continuing.

USFMAE-IS can help by identifying hold risk before it becomes a problem. The app should show:

- current balance,
- overdue charges,
- due soon charges,
- payment status,
- hold risk level,
- recommended next action.

A useful student-facing message could be:

> Your current balance is $1,250. Two charges are due within 10 days. Please make a payment or contact Student Financial Services to avoid registration delay.

This makes the system more practical than a simple balance table.

### 5. Payment Plans Are A Real Student Need

Universities often offer term-based payment plans. These plans spread balances across installments and help students avoid large immediate payments. Stanford, Case Western Reserve, Drexel, University of Cincinnati, and NC State all describe online payment plans or billing tools.

USFMAE-IS can add a simplified payment plan feature:

- payment plan name,
- student,
- total plan amount,
- number of installments,
- installment due dates,
- installment status,
- remaining amount.

This would make the system more useful for students who cannot pay the full balance at once.

## Detailed Feature Plan

### Feature 1: Student Login And Private Profile

Status: Already started.

Purpose:

Students should only see their own information, not everyone else’s. This makes the system more realistic and protects student financial data.

Requirements:

- Each student links to a login user.
- Students log in at `/login/`.
- Students see `/my-profile/`.
- Students cannot access other students’ records.
- Staff can access administrative pages.

Student-facing profile should show:

- name,
- email,
- major,
- GPA,
- enrollment status,
- charges,
- payments,
- balance,
- aid applications,
- required documents,
- action items.

### Feature 2: Financial Aid Document Checklist

Purpose:

Students need to know exactly what is missing.

Tables:

- RequiredDocument
- ApplicationDocument

Student view:

- Document name
- Status
- Received date
- Notes

Admin view:

- Add required documents to an application.
- Mark document as required, submitted, accepted, rejected, or waived.
- Add review notes.

This feature directly covers missing-document delays.

### Feature 3: Action Items / To-Do List

Purpose:

Convert database information into clear next steps.

Examples:

- Missing FAFSA confirmation.
- Missing income verification.
- Balance due soon.
- Payment plan needed.
- Application needs review.
- Enrollment status needs confirmation.

Dashboard:

- Student sees their open action items.
- Staff sees urgent/open action items across all students.

This is probably the most student-useful feature in the system.

### Feature 4: Hold Risk Indicator

Purpose:

Warn students before unpaid balances cause registration problems.

Suggested logic:

- No risk: balance is zero or all charges are future due.
- Low risk: balance exists but no due date is near.
- Medium risk: charge due within 14 days.
- High risk: charge is overdue.

Student message:

- “No current hold risk.”
- “Balance due soon.”
- “Overdue balance: contact Student Financial Services.”

Admin report:

- list of students at high risk,
- amount overdue,
- due date,
- recommended action.

### Feature 5: Aid Status Timeline

Purpose:

Make aid processing stages understandable.

Possible stages:

1. Application submitted.
2. Documents requested.
3. Documents received.
4. Under review.
5. Eligible.
6. Approved.
7. Award applied to balance.
8. Completed or denied.

This is useful because students often do not understand the difference between “aid application submitted,” “award approved,” and “funds applied to bill.”

### Feature 6: Filtered Reports

Purpose:

Help administrators make decisions.

Filters:

- semester,
- balance above amount,
- overdue only,
- aid status,
- missing documents,
- payment method,
- date range.

Reports:

- balance report,
- overdue balance report,
- payment summary,
- aid document report,
- action item report,
- eligibility report.

### Feature 7: Payment Plan Prototype

Purpose:

Help students understand how they can handle a balance over time.

Tables:

- PaymentPlan
- PaymentInstallment

Fields:

- student,
- plan amount,
- start date,
- installment amount,
- due date,
- status,
- paid date.

Student view:

- installment schedule,
- paid/unpaid status,
- remaining balance.

### Feature 8: Notifications And Email Simulation

Purpose:

Show that the system can alert students.

Simple class-project version:

- notification table,
- notification list on profile,
- no real email required.

Examples:

- “Income verification is due by Feb 10.”
- “Payment received: $1,500.”
- “Aid application moved to under review.”

## Priority Recommendation

### Build First

1. Student login/private profile.
2. Required document checklist.
3. Action items.

These are the most important because they directly improve student usefulness and make the app realistic.

### Build Second

4. Hold risk indicator.
5. Aid status timeline.
6. Filtered reports.

These make the system more decision-ready.

### Build Later

7. Payment plan prototype.
8. Notifications.
9. Report export.
10. README screenshots.

These add polish after the core workflow is strong.

## Database Changes Needed

Already added or recommended:

- link Student to Django User,
- ActionItem,
- RequiredDocument,
- ApplicationDocument.

Recommended next tables:

- AidStatusEvent,
- PaymentPlan,
- PaymentInstallment,
- Notification.

## How This Makes The App More Useful

For students:

- They log in and see only their own information.
- They understand what they owe.
- They know which documents are missing.
- They know what action to take next.
- They can see whether aid is actually helping their balance.

For administrators:

- They can see students at risk.
- They can track document status.
- They can review applications faster.
- They can generate more meaningful reports.

For a class presentation:

- The app becomes easier to explain.
- The database design looks more mature.
- The workflow looks closer to a real university system.
- The project solves a real problem instead of only displaying records.

## Final Recommendation

USFMAE-IS should become a student-centered finance portal. The best next phrase for the project is:

> USFMAE-IS helps students understand balances, aid requirements, missing documents, and next steps while helping administrators monitor financial risk and aid readiness.

This framing is stronger, more realistic, and easier to defend in a project presentation.
