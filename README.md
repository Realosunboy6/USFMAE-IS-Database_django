# USFMAE-IS Database

USFMAE-IS means **University Student Financial Management & Aid Eligibility Information System**. This database supports a student finance system for tracking tuition charges, payments, student balances, scholarships, financial aid applications, and administrator reviews.

The purpose of the database is to give students and administrators one organized place to manage student financial information. Students can understand what they owe, what they have paid, and the status of their aid applications. Administrators can record charges, verify payments, review aid requests, and prepare useful financial reports.

## Database Purpose

This database is designed to solve a common university problem: student financial information is often spread across different records, making it difficult for students to understand their balance and difficult for staff to review aid applications efficiently.

USFMAE-IS organizes that information into connected tables so the system can answer questions such as:

- Which students have outstanding balances?
- What charges have been assigned to each student?
- What payments has each student made?
- Which students submitted aid applications?
- Which applications are pending, approved, denied, or missing documents?
- Which students meet the basic scholarship eligibility rules?

## Main Tables

### Student

Stores student profile information used for financial tracking and aid review.

Fields include:

- Student ID
- First name
- Last name
- Email
- Major
- GPA
- Enrollment status

### Fee Category

Stores the types of fees that can be charged to students.

Fields include:

- Fee ID
- Fee name
- Standard amount
- Semester

### Student Charge

Connects students to the fees they have been charged. This table represents the relationship between a student and a fee category.

Fields include:

- Student
- Fee category
- Charge amount
- Due date

### Payment

Stores payments made by students.

Fields include:

- Payment ID
- Student
- Payment date
- Amount
- Payment method
- Receipt number

### Scholarship

Stores scholarship or financial aid program information.

Fields include:

- Scholarship ID
- Scholarship name
- Award type
- Award amount
- GPA requirement
- Enrollment requirement

### Aid Application

Stores student applications for scholarships or financial aid.

Fields include:

- Application ID
- Student
- Scholarship
- Application date
- Documents submitted
- Application status
- Reviewing administrator

### Administrator

Stores administrator information for staff who review aid applications.

Fields include:

- Admin ID
- First name
- Last name
- Role

## Relationships

The database uses these main relationships:

- One student can have many payments.
- One student can have many assigned charges.
- One fee category can be assigned to many students.
- One student can submit many aid applications.
- One scholarship can have many aid applications.
- One administrator can review many aid applications.

## Reports Supported

The database supports important student finance reports:

- Student balance report
- Payment summary report
- Aid application status report
- Scholarship eligibility review
- Student financial profile

## School-Readiness Direction

The long-term goal is to grow USFMAE-IS from a class-project prototype into a student finance clarity system that schools could seriously evaluate. In that version, students would log in and clearly understand:

- what they owe,
- what they have paid,
- what aid is pending,
- which documents are missing,
- whether they are at risk of a registration or account hold,
- what action they need to complete next.

Administrators would use the system to review balances, track missing documents, manage aid application decisions, assign action items, and generate decision-ready reports.

To become usable by real schools, the project needs more than extra screens. The next major work should focus on trust and operations:

- production settings with environment-based secrets,
- stronger role-based access control,
- audit logs for sensitive student record access and changes,
- secure document upload and storage,
- workflow history for aid reviews and action items,
- school identity login such as SSO,
- integrations with student information, billing, and financial aid systems,
- backup, monitoring, incident-response, and data-retention procedures.

A fuller school-readiness assessment is available in `outputs/school_readiness_assessment.md`.

## Sample Data

The database includes sample data for demonstration. The sample records include students, fee charges, payments, scholarships, and aid applications. The student sample data uses distinct Nigerian names so the demonstration looks realistic and professional.

## Running The Project

Start the Django app with:

```bash
cd /Users/isye/Downloads/usfmae_django
source .venv/bin/activate
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Scope

This is currently a class project database prototype. The aid eligibility feature uses simple rules based on GPA, enrollment status, and document submission. It is meant to support basic review and reporting, not replace a full official university financial aid system yet.

The planned direction is to make the system more useful and realistic for schools by adding stronger privacy controls, auditability, integrations, secure workflows, and production deployment practices.
