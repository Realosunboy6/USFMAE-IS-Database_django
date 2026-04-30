# Provenance: USFMAE-IS Django Review

Date: 2026-04-30

## Files Reviewed

- `finance/models.py`
- `finance/views.py`
- `finance/services.py`
- `finance/management/commands/import_access_data.py`
- `finance/management/commands/seed_demo_data.py`
- `finance/templates/finance/student_list.html`
- `README.md`

## Changes Made During Review

### `finance/management/commands/import_access_data.py`

Reason:

- Access/CSV exports may contain display values rather than Django internal choice constants.

Changes:

- Added `normalize_key`.
- Added `normalize_choice`.
- Added `parse_bool`.
- Normalized enrollment status, award type, enrollment requirement, payment method, and aid application status.

### `finance/tests.py`

Reason:

- The project needed repeatable verification beyond manual route checks.

Changes:

- Added model tests for balance and eligibility.
- Added route tests.
- Added student search test.
- Added demo seed idempotence test.
- Added Access/CSV import normalization test.

### `finance/views.py`

Reason:

- The student list became less usable after adding 100 sample students.

Changes:

- Added search with `Q` filters.
- Added pagination with 25 students per page.
- Added query context for preserving search state.

### `finance/templates/finance/student_list.html`

Reason:

- Needed UI for search and pagination.

Changes:

- Added search form.
- Added clear link.
- Added previous/next pagination controls.

### `README.md`

Reason:

- Documentation needed to reflect the current prepared state and improvements.

Changes:

- Added test command to the verification block.
- Clarified that demo seed data includes 100 Nigerian sample students.
- Updated feature list to mention searchable, paginated student list.

## Verification Commands

```bash
.venv/bin/python manage.py test
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
```

## Verification Results

- `manage.py test`: 6 tests passed.
- `manage.py check`: no issues.
- `makemigrations --check --dry-run`: no changes detected.

## Limitations

- This review did not inspect the binary `.accdb` files directly because local Access inspection tooling was not installed.
- The review focused on local demo readiness, not production hardening.
- Authentication and role-based permissions are still recommended for a more realistic deployment.
