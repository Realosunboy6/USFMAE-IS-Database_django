<img width="2530" height="1494" alt="image" src="https://github.com/user-attachments/assets/f4c5957b-e72a-49f2-b94e-b3374cd4290c" />


# USFMAE-IS Database

USFMAE-IS means **University Student Financial Management and Aid Eligibility Information System**. It is a Django web application for tracking student finance records, aid applications, required documents, action items, payments, charges, reports, and student profile information.

The project started as a class database prototype and is now being developed toward a more realistic **student finance clarity dashboard**: a system that helps students understand what they owe, what they have paid, what aid is pending, what documents are missing, and what action they need to complete next.

## What The App Does

USFMAE-IS supports two main user experiences:

- **Students** can log in, view their own profile, see charges and payments, check aid application status, view action items, and upload profile-related documents.
- **Finance and aid staff** can review student records, manage charges and payments, track aid applications, manage required documents, create action items, view reports, and inspect audit logs.

The app currently includes:

- student profile pages,
- student profile editing,
- staff profile creation and editing,
- student document upload, review, download, and archive flows,
- role-based access groups,
- audit logging for sensitive actions,
- student charges and payments,
- scholarship and aid application tracking,
- required-document checklist tracking,
- action items / student to-do tasks,
- reports for balances, aid status, documents, hold risk, and payments,
- demo data seeding for local testing,
- NIU-inspired red/black/white visual direction.

## Project Status

This is still a prototype, not a production university system.

It is useful for demonstrating how a student finance clarity portal could work, but a real school deployment would still need stronger security, production hosting, official system integrations, private file storage, accessibility review, FERPA/GLBA compliance review, and institutional approval.

Research and planning notes are included in:

- `outputs/school_readiness_assessment.md`
- `outputs/niu_adoption_deep_research.md`
- `outputs/niu_adoption_redteam.md`

## Tech Stack

- Python
- Django 5
- SQLite for local development
- Django templates
- Django authentication, groups, and permissions

## Main App Structure

```text
usfmae_django/
├── finance/
│   ├── models.py                  # database models
│   ├── views.py                   # page and workflow views
│   ├── forms.py                   # Django forms
│   ├── urls.py                    # app routes
│   ├── rbac.py                    # role/permission setup
│   ├── signals.py                 # audit logging hooks
│   ├── middleware.py              # current-user audit context
│   ├── templates/finance/         # app pages
│   └── management/commands/       # demo data and CSV import commands
├── usfmae_django/
│   ├── settings.py                # project settings
│   └── urls.py                    # project URL router
├── outputs/                       # research, roadmap, and review docs
├── papers/                        # planning/research notes
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Clone And Run Locally

These steps assume you have Python installed. Python 3.11 or newer is recommended.

### 1. Clone the repository

```bash
git clone https://github.com/Realosunboy6/USFMAE-IS-Database_django.git
cd USFMAE-IS-Database_django
```

If you cloned from the older repository URL, GitHub may redirect it. The current repository location is:

```text
https://github.com/Realosunboy6/USFMAE-IS-Database_django
```

### 2. Create and activate a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create your local environment file

Copy the example file:

```bash
cp .env.example .env
```

For local development, the defaults are enough. For deployment, change the secret key and security settings.

Important environment variables:

```text
DJANGO_SECRET_KEY=change-me-before-deploying
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CSRF_TRUSTED_ORIGINS=
DJANGO_SESSION_COOKIE_SECURE=0
DJANGO_CSRF_COOKIE_SECURE=0
DJANGO_SECURE_SSL_REDIRECT=0
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Seed demo data

```bash
python manage.py seed_demo_data
```

This creates demo students, charges, payments, scholarships, aid applications, action items, documents, role groups, and test login users.

### 7. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

If port `8000` is busy, run another port:

```bash
python manage.py runserver 127.0.0.1:8010
```

Then open:

```text
http://127.0.0.1:8010/
```

## Demo Login Accounts

After running `python manage.py seed_demo_data`, use:

```text
Staff user:
username: staff
password: StaffPass123!

Student user:
username: student10
password: StudentPass123!
```

Staff users can access dashboard, reports, student lists, action items, aid review, documents, and audit logs depending on their assigned finance group.

Student users are redirected to their own profile and cannot view other students' profiles.

## Useful Local Commands

Run tests:

```bash
python manage.py test
```

Run Django system checks:

```bash
python manage.py check
```

Check whether migrations are missing:

```bash
python manage.py makemigrations --check --dry-run
```

Create an admin/superuser account:

```bash
python manage.py createsuperuser
```

Import CSV data exported from an Access-style database:

```bash
python manage.py import_access_data path/to/csv_folder
```

Expected CSV names include:

- `Student.csv`
- `Administrator.csv`
- `FeeCategory.csv`
- `Scholarship.csv`
- `IsCharged.csv`
- `Payment.csv`
- `AidApplication.csv`

## Main Routes

```text
/                         staff dashboard
/login/                   login page
/logout/                  logout
/my-profile/              current student's profile
/my-profile/edit/         student self-service profile edit
/students/                staff student directory
/students/new/            staff create student profile
/students/<id>/           student profile detail
/students/<id>/edit/      staff edit student profile
/charges/                 manage charges
/payments/                manage payments
/action-items/            manage student action items
/aid-applications/        manage aid applications
/aid-documents/           manage aid document checklist
/reports/                 reports
/audit-log/               audit log
/export/audit-bundle/     audit CSV bundle download
```

## Current Data Model Summary

Important models include:

- `Student`
- `StudentProfileDetails`
- `StudentUploadedDocument`
- `FeeCategory`
- `StudentCharge`
- `Payment`
- `Scholarship`
- `AidApplication`
- `RequiredDocument`
- `ApplicationDocument`
- `ActionItem`
- `Administrator`
- `ImportBatch`
- `AuditLog`
- `FinanceDivision`

## Security Notes

The app includes early security and privacy features:

- Django authentication,
- role-based finance groups,
- student-only profile access,
- staff-only administrative workflows,
- protected document download views,
- audit logging for sensitive actions,
- environment-based settings.

However, production use would still require:

- real private media storage,
- HTTPS-only deployment,
- MFA or school SSO,
- structured audit reasons,
- IP and user-agent fields,
- malware scanning for uploads,
- backup and retention policies,
- FERPA/GLBA review,
- accessibility review,
- formal security testing.

## NIU / School-Readiness Direction

The current product direction is not to replace a university's official student information, billing, or financial aid systems. A realistic school adoption path is to use this as a **student finance clarity layer** that imports or reads approved official data and explains it clearly to students and staff.

For an NIU-style version, the student-facing product could be called:

```text
Huskie Finance Clarity
```

The UI direction should continue using:

- NIU Red: `#C8102E`
- Black: `#000000`
- Gray: `#A5A7A8`
- White: `#FFFFFF`
- clean sans-serif typography

## Troubleshooting

If `python manage.py runserver` says the port is already in use, choose another port:

```bash
python manage.py runserver 127.0.0.1:8010
```

If login does not work, make sure demo data was seeded:

```bash
python manage.py seed_demo_data
```

If database tables are missing, run migrations:

```bash
python manage.py migrate
```

If dependencies are missing, activate the virtual environment and reinstall:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## License / Use

This repository is currently a student/class project prototype. Do not use it with real student data without production security hardening, institutional approval, and compliance review.
