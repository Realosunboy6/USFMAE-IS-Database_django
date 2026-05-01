# Provenance: USFMAE-IS Student Usefulness Plan

Date: 2026-04-30

## Workflow Notes

- The `alpha` CLI was not available directly on PATH, so academic-paper search through `alpha` could not be used.
- The `paper-writing` and `peer-review` prompt templates referenced by the skills were not present at the expected paths.
- The work still followed the intended process:
  1. research,
  2. draft a detailed plan,
  3. review the plan,
  4. improve the recommendations.

## Local App Context

Reviewed current USFMAE-IS implementation:

- `finance/models.py`
- `finance/views.py`
- `finance/forms.py`
- `finance/services.py`
- `finance/templates/finance/*.html`
- `README.md`

Current app capabilities:

- student records,
- charges,
- payments,
- balances,
- scholarships,
- aid applications,
- action items,
- document tracking,
- reports,
- student login/private profile work in progress.

## External Research Sources

### Student Financial Services Portals

Search:

`student financial services portal features balance payment history financial aid status university`

Used for:

- balance and payment history features,
- student billing transparency,
- aid status visibility,
- authorized/proxy access ideas,
- payment plan feature ideas.

### Financial Aid Document Tracking

Search:

`financial aid verification missing documents student portal to do list university`

Used for:

- verification document requirements,
- To-Do lists,
- missing document workflows,
- consequences of late or missing documents.

Examples included:

- University of Colorado Boulder verification guidance,
- Boise State verification guidance,
- Florida State verification guidance,
- Florida Atlantic verification guidance,
- University of South Florida verification documentation.

### Registration Holds and Unpaid Balances

Search:

`college students unpaid balances registration holds re-enrollment financial barriers research`

Used for:

- hold risk,
- unpaid balance consequences,
- registration delay,
- transcript/stranded credit concerns,
- disproportionate impact on vulnerable students.

Sources surfaced:

- Inside Higher Ed coverage of registration hold disparities,
- AACRAO/Lumina reporting,
- Ithaka S+R stranded credits discussion,
- Education Commission of the States report on holds.

### Payment Plans and Financial Wellness

Search:

`student financial wellness transparency billing payment plans university portal features`

Used for:

- payment plan ideas,
- installment tracking,
- student billing transparency,
- automatic balance adjustment concepts.

Examples surfaced:

- University of Cincinnati,
- Case Western Reserve,
- Drexel,
- Stanford,
- NC State.

## Main Claims Supported

### Claim: Missing documents are a major aid-processing blocker.

Supported by:

- university verification pages showing required documents and To-Do list workflows.

### Claim: Students need plain-language next steps.

Supported by:

- portal To-Do list patterns and action item workflows.

### Claim: Balances and holds can affect registration and progress.

Supported by:

- registration hold research and stranded credit discussions.

### Claim: Payment plans are useful but should be later.

Supported by:

- university payment plan examples and complexity tradeoff.

## Deliverables Created

- `papers/usfmae_student_usefulness_plan.md`
- `outputs/usfmae_student_usefulness_review.md`
- `outputs/usfmae_student_usefulness_plan.provenance.md`
