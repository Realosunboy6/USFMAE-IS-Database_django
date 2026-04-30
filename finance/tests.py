import csv
from datetime import date
from decimal import Decimal
from tempfile import TemporaryDirectory
from pathlib import Path

from django.core.management import call_command
from django.test import Client, TestCase

from .models import AidApplication, FeeCategory, Payment, Scholarship, Student, StudentCharge


class FinanceModelTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            first_name="Amina",
            last_name="Balogun",
            email="amina.balogun@example.edu",
            major="Information Systems",
            gpa=Decimal("3.75"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        self.fee = FeeCategory.objects.create(
            fee_name="Tuition",
            standard_amount=Decimal("4500.00"),
            semester="Spring 2026",
        )
        self.scholarship = Scholarship.objects.create(
            scholarship_name="Merit Excellence Scholarship",
            award_type=Scholarship.AwardType.MERIT,
            award_amount=Decimal("1500.00"),
            gpa_requirement=Decimal("3.50"),
            enrollment_requirement=Student.EnrollmentStatus.FULL_TIME,
        )

    def test_current_balance_uses_charges_minus_payments(self):
        StudentCharge.objects.create(
            student=self.student,
            fee=self.fee,
            amount=Decimal("4500.00"),
            due_date=date(2026, 2, 15),
        )
        Payment.objects.create(
            student=self.student,
            payment_date=date(2026, 1, 20),
            amount=Decimal("1200.00"),
            method=Payment.Method.CARD,
            receipt_no="R-T-001",
        )

        self.assertEqual(self.student.current_balance, Decimal("3300.00"))

    def test_basic_eligibility_requires_gpa_enrollment_and_documents(self):
        application = AidApplication.objects.create(
            student=self.student,
            scholarship=self.scholarship,
            application_date=date(2026, 1, 18),
            docs_submitted=True,
        )

        self.assertTrue(application.meets_basic_eligibility)


class FinanceRouteTests(TestCase):
    def test_main_pages_load(self):
        client = Client()
        for path in ["/", "/students/", "/charges/", "/payments/", "/aid-applications/", "/reports/"]:
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 200)

    def test_student_search_loads(self):
        Student.objects.create(
            first_name="Chidera",
            last_name="Nwosu",
            email="chidera.nwosu@example.edu",
            major="Statistics",
            gpa=Decimal("3.20"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )

        response = Client().get("/students/", {"q": "Chidera"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chidera Nwosu")


class SeedDemoDataTests(TestCase):
    def test_seed_demo_data_is_idempotent_and_adds_nigerian_samples(self):
        call_command("seed_demo_data", verbosity=0)
        call_command("seed_demo_data", verbosity=0)

        self.assertEqual(Student.objects.filter(student_id__gte=10, student_id__lte=109).count(), 100)
        self.assertGreaterEqual(StudentCharge.objects.count(), 100)
        self.assertGreaterEqual(Payment.objects.count(), 50)
        self.assertGreaterEqual(AidApplication.objects.count(), 30)


class ImportAccessDataTests(TestCase):
    def write_csv(self, folder, filename, rows):
        path = folder / filename
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def test_import_accepts_human_readable_choice_values(self):
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            self.write_csv(
                folder,
                "Student.csv",
                [
                    {
                        "StudentID": "1",
                        "FirstName": "Chiamaka",
                        "LastName": "Okeke",
                        "Email": "chiamaka.okeke@example.edu",
                        "Major": "Statistics",
                        "GPA": "3.80",
                        "EnrollmentStatus": "Full Time",
                    }
                ],
            )
            self.write_csv(
                folder,
                "Administrator.csv",
                [{"AdminID": "1", "FirstName": "Ibrahim", "LastName": "Oyeyinka", "Role": "Reviewer"}],
            )
            self.write_csv(
                folder,
                "FeeCategory.csv",
                [{"FeeID": "1", "FeeName": "Tuition", "StandardAmount": "4500", "Semester": "Spring 2026"}],
            )
            self.write_csv(
                folder,
                "Scholarship.csv",
                [
                    {
                        "ScholarshipID": "1",
                        "ScholarshipName": "Access Grant",
                        "AwardType": "Need Based",
                        "AwardAmount": "1000",
                        "GPARequirement": "2.50",
                        "EnrollmentRequirement": "Full Time",
                    }
                ],
            )
            self.write_csv(
                folder,
                "IsCharged.csv",
                [{"StudentID": "1", "FeeID": "1", "Amount": "$4,500.00", "DueDate": "02/15/2026"}],
            )
            self.write_csv(
                folder,
                "Payment.csv",
                [
                    {
                        "PaymentID": "1",
                        "PaymentDate": "2026-01-20",
                        "Amount": "1500",
                        "Method": "Bank Transfer",
                        "ReceiptNo": "R-IMPORT-1",
                        "StudentID": "1",
                    }
                ],
            )
            self.write_csv(
                folder,
                "AidApplication.csv",
                [
                    {
                        "ApplicationID": "1",
                        "ApplicationDate": "01/22/2026",
                        "DocsSubmitted": "Submitted",
                        "Status": "Needs Documents",
                        "StudentID": "1",
                        "ScholarshipID": "1",
                        "AdminID": "1",
                    }
                ],
            )

            call_command("import_access_data", folder, verbosity=0)

        student = Student.objects.get(student_id=1)
        payment = Payment.objects.get(payment_id=1)
        application = AidApplication.objects.get(application_id=1)

        self.assertEqual(student.enrollment_status, Student.EnrollmentStatus.FULL_TIME)
        self.assertEqual(payment.method, Payment.Method.BANK_TRANSFER)
        self.assertEqual(application.status, AidApplication.Status.NEEDS_DOCUMENTS)
        self.assertTrue(application.docs_submitted)
