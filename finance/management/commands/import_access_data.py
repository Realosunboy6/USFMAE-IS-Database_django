import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from finance.models import (
    Administrator,
    AidApplication,
    FeeCategory,
    Payment,
    Scholarship,
    Student,
    StudentCharge,
)


def parse_date(value):
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def parse_decimal(value):
    return Decimal(str(value).replace("$", "").replace(",", "").strip())


def normalize_key(value):
    return str(value).strip().replace("-", " ").replace("_", " ").lower()


def normalize_choice(value, choices, field_name):
    lookup = {}
    for database_value, display_value in choices:
        lookup[normalize_key(database_value)] = database_value
        lookup[normalize_key(display_value)] = database_value
    key = normalize_key(value)
    if key not in lookup:
        valid_values = ", ".join(display for _, display in choices)
        raise CommandError(f"Unsupported {field_name}: {value}. Expected one of: {valid_values}")
    return lookup[key]


def parse_bool(value):
    return normalize_key(value) in {"true", "yes", "y", "1", "submitted"}


class Command(BaseCommand):
    help = "Import CSV files exported from the Access database into the Django SQLite database."

    def add_arguments(self, parser):
        parser.add_argument("csv_dir", type=Path, help="Directory containing exported CSV files.")

    def handle(self, *args, **options):
        csv_dir = options["csv_dir"]
        if not csv_dir.exists():
            raise CommandError(f"CSV directory does not exist: {csv_dir}")

        self.import_students(csv_dir / "Student.csv")
        self.import_administrators(csv_dir / "Administrator.csv")
        self.import_fee_categories(csv_dir / "FeeCategory.csv")
        self.import_scholarships(csv_dir / "Scholarship.csv")
        self.import_charges(csv_dir / "IsCharged.csv")
        self.import_payments(csv_dir / "Payment.csv")
        self.import_aid_applications(csv_dir / "AidApplication.csv")

        self.stdout.write(self.style.SUCCESS("Import complete."))

    def rows(self, path):
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"Skipping missing file: {path.name}"))
            return []
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))

    def import_students(self, path):
        for row in self.rows(path):
            Student.objects.update_or_create(
                student_id=row["StudentID"],
                defaults={
                    "first_name": row["FirstName"],
                    "last_name": row["LastName"],
                    "email": row["Email"],
                    "major": row["Major"],
                    "gpa": parse_decimal(row["GPA"]),
                    "enrollment_status": normalize_choice(
                        row["EnrollmentStatus"],
                        Student.EnrollmentStatus.choices,
                        "enrollment status",
                    ),
                },
            )

    def import_administrators(self, path):
        for row in self.rows(path):
            Administrator.objects.update_or_create(
                admin_id=row["AdminID"],
                defaults={
                    "first_name": row["FirstName"],
                    "last_name": row["LastName"],
                    "role": row["Role"],
                },
            )

    def import_fee_categories(self, path):
        for row in self.rows(path):
            FeeCategory.objects.update_or_create(
                fee_id=row["FeeID"],
                defaults={
                    "fee_name": row["FeeName"],
                    "standard_amount": parse_decimal(row["StandardAmount"]),
                    "semester": row["Semester"],
                },
            )

    def import_scholarships(self, path):
        for row in self.rows(path):
            Scholarship.objects.update_or_create(
                scholarship_id=row["ScholarshipID"],
                defaults={
                    "scholarship_name": row["ScholarshipName"],
                    "award_type": normalize_choice(row["AwardType"], Scholarship.AwardType.choices, "award type"),
                    "award_amount": parse_decimal(row["AwardAmount"]),
                    "gpa_requirement": parse_decimal(row["GPARequirement"]),
                    "enrollment_requirement": normalize_choice(
                        row["EnrollmentRequirement"],
                        Student.EnrollmentStatus.choices,
                        "enrollment requirement",
                    ),
                },
            )

    def import_charges(self, path):
        for row in self.rows(path):
            StudentCharge.objects.update_or_create(
                student_id=row["StudentID"],
                fee_id=row["FeeID"],
                defaults={
                    "amount": parse_decimal(row["Amount"]),
                    "due_date": parse_date(row["DueDate"]),
                },
            )

    def import_payments(self, path):
        for row in self.rows(path):
            Payment.objects.update_or_create(
                payment_id=row["PaymentID"],
                defaults={
                    "student_id": row["StudentID"],
                    "payment_date": parse_date(row["PaymentDate"]),
                    "amount": parse_decimal(row["Amount"]),
                    "method": normalize_choice(row["Method"], Payment.Method.choices, "payment method"),
                    "receipt_no": row["ReceiptNo"],
                },
            )

    def import_aid_applications(self, path):
        for row in self.rows(path):
            AidApplication.objects.update_or_create(
                application_id=row["ApplicationID"],
                defaults={
                    "student_id": row["StudentID"],
                    "scholarship_id": row["ScholarshipID"],
                    "administrator_id": row.get("AdminID") or None,
                    "application_date": parse_date(row["ApplicationDate"]),
                    "docs_submitted": parse_bool(row["DocsSubmitted"]),
                    "status": normalize_choice(row["Status"], AidApplication.Status.choices, "application status"),
                },
            )
