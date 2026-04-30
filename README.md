# USFMAE-IS Django Project

University Student Financial Management & Aid Eligibility Information System (USFMAE-IS) is a Django version of the class project Access database prototype.

The project solves a practical student finance problem: students need a clear place to see tuition charges, payments, current balance, and aid status, while administrators need faster tools for recording payments, reviewing aid applications, and generating reports.

## Source Database

The original files are in:

```text
/Users/isye/Downloads/DATABASE
```

Detected Access files:

- `OYELAB1.accdb`
- `OYELAB2.accdb`
- `OYELAB4.accdb`

The Django schema is based on the normalized class-project documents in the same folder. Direct `.accdb` inspection requires Access-compatible tooling such as `mdbtools`, ODBC, Microsoft Access, or export to CSV.

## Data Model

The Django app maps the documented 3NF schema:

- `Student`
- `Payment`
- `FeeCategory`
- `StudentCharge` for the Access relation `IsCharged`
- `Scholarship`
- `AidApplication`
- `Administrator`

## Project Structure

```text
usfmae_django/
  manage.py
  requirements.txt
  README.md
  usfmae_django/
    settings.py
    urls.py
    asgi.py
    wsgi.py
  finance/
    models.py
    admin.py
    forms.py
    services.py
    views.py
    urls.py
    management/commands/import_access_data.py
    templates/finance/
```

## Setup

Create and activate a virtual environment:

```bash
cd /Users/isye/Downloads/usfmae_django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create the database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

Create an admin user:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Open:

- Main app: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## Importing Data From Access

If Microsoft Access or another tool can export the tables to CSV, use these filenames:

```text
Student.csv
Administrator.csv
FeeCategory.csv
Scholarship.csv
IsCharged.csv
Payment.csv
AidApplication.csv
```

Then run:

```bash
python manage.py import_access_data /path/to/exported/csvs
```

Expected column names follow the class schema:

- `StudentID`, `FirstName`, `LastName`, `Email`, `Major`, `GPA`, `EnrollmentStatus`
- `PaymentID`, `PaymentDate`, `Amount`, `Method`, `ReceiptNo`, `StudentID`
- `FeeID`, `FeeName`, `StandardAmount`, `Semester`
- `StudentID`, `FeeID`, `Amount`, `DueDate`
- `ScholarshipID`, `ScholarshipName`, `AwardType`, `AwardAmount`, `GPARequirement`, `EnrollmentRequirement`
- `ApplicationID`, `ApplicationDate`, `DocsSubmitted`, `Status`, `StudentID`, `ScholarshipID`, `AdminID`
- `AdminID`, `FirstName`, `LastName`, `Role`

## Views Included

- Dashboard with totals and pending applications.
- Student list and student financial profile.
- Charge assignment.
- Payment recording and history.
- Aid application submission.
- Administrator aid review.
- Balance, payment, and aid status reports.

## Scope Note

The aid eligibility helper is intentionally simplified for a class project. It checks GPA, enrollment status, and document submission. It should not be presented as an official financial aid determination engine.
