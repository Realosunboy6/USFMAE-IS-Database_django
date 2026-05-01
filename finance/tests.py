import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from .models import (
    ActionItem,
    AidApplication,
    ApplicationDocument,
    AuditLog,
    FeeCategory,
    ImportBatch,
    Payment,
    RequiredDocument,
    Scholarship,
    Student,
    StudentCharge,
    StudentProfileDetails,
    StudentUploadedDocument,
)
from .rbac import (
    GROUP_AUDITOR,
    GROUP_BURSAR,
    GROUP_FINANCIAL_AID,
    GROUP_SUPERVISOR,
    setup_finance_groups,
)


def attach_group(user: User, group_name: str) -> None:
    setup_finance_groups()
    user.groups.set([Group.objects.get(name=group_name)])


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

    def test_application_document_tracks_required_document_status(self):
        application = AidApplication.objects.create(
            student=self.student,
            scholarship=self.scholarship,
            application_date=date(2026, 1, 18),
            docs_submitted=True,
        )
        required_document = RequiredDocument.objects.create(
            document_name="Academic Transcript",
            applies_to_award_type=Scholarship.AwardType.MERIT,
        )

        document = ApplicationDocument.objects.create(
            application=application,
            required_document=required_document,
            status=ApplicationDocument.Status.SUBMITTED,
            received_date=date(2026, 1, 19),
        )

        self.assertEqual(document.status, ApplicationDocument.Status.SUBMITTED)

    def test_checklist_overrides_documents_submitted_flag(self):
        application = AidApplication.objects.create(
            student=self.student,
            scholarship=self.scholarship,
            application_date=date(2026, 1, 18),
            docs_submitted=True,
        )
        required_document = RequiredDocument.objects.create(
            document_name="FAFSA Confirmation",
            applies_to_award_type=Scholarship.AwardType.MERIT,
        )
        ApplicationDocument.objects.create(
            application=application,
            required_document=required_document,
            status=ApplicationDocument.Status.REQUIRED,
        )
        application.refresh_from_db()
        self.assertFalse(application.docs_submitted)
        self.assertFalse(application.documents_satisfied_from_records())

        checklist = ApplicationDocument.objects.get(application=application, required_document=required_document)
        checklist.status = ApplicationDocument.Status.ACCEPTED
        checklist.save(update_fields=["status"])
        application.refresh_from_db()
        self.assertTrue(application.docs_submitted)
        self.assertTrue(application.documents_satisfied_from_records())


class FinanceRouteTests(TestCase):
    def test_main_pages_load(self):
        staff = User.objects.create_user(username="staff", password="StaffPass123!", is_staff=True)
        attach_group(staff, GROUP_SUPERVISOR)
        client = Client()
        client.force_login(staff)
        for path in [
            "/",
            "/students/",
            "/charges/",
            "/payments/",
            "/action-items/",
            "/aid-applications/",
            "/aid-documents/",
            "/reports/",
            "/audit-log/",
            "/export/audit-bundle/",
        ]:
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 200)

    def test_student_search_loads(self):
        staff = User.objects.create_user(username="staff", password="StaffPass123!", is_staff=True)
        attach_group(staff, GROUP_SUPERVISOR)
        Student.objects.create(
            first_name="Chidera",
            last_name="Nwosu",
            email="chidera.nwosu@example.edu",
            major="Statistics",
            gpa=Decimal("3.20"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )

        client = Client()
        client.force_login(staff)
        response = client.get("/students/", {"q": "Chidera"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Chidera Nwosu")

    def test_student_can_only_view_own_profile(self):
        user_one = User.objects.create_user(username="student1", password="StudentPass123!")
        user_two = User.objects.create_user(username="student2", password="StudentPass123!")
        student_one = Student.objects.create(
            user=user_one,
            first_name="Amina",
            last_name="Balogun",
            email="amina.balogun@example.edu",
            major="Information Systems",
            gpa=Decimal("3.75"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        student_two = Student.objects.create(
            user=user_two,
            first_name="Chidera",
            last_name="Nwosu",
            email="chidera.nwosu@example.edu",
            major="Statistics",
            gpa=Decimal("3.20"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        client = Client()
        client.force_login(user_one)

        self.assertEqual(client.get("/my-profile/").status_code, 200)
        self.assertEqual(client.get(f"/students/{student_one.student_id}/").status_code, 200)
        self.assertEqual(client.get(f"/students/{student_two.student_id}/").status_code, 403)


class RoleBasedAccessTests(TestCase):
    def test_bursar_cannot_manage_aid(self):
        Student.objects.create(
            first_name="Role",
            last_name="Tester",
            email="role.bursar@example.edu",
            major="Industrial Engineering",
            gpa=Decimal("3.00"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        user = User.objects.create_user(username="bursar", password="Pwd12345!", is_staff=False)
        attach_group(user, GROUP_BURSAR)
        client = Client()
        client.force_login(user)
        self.assertEqual(client.get("/aid-applications/").status_code, 403)
        self.assertEqual(client.get("/payments/").status_code, 200)
        self.assertEqual(client.get("/reports/").status_code, 200)

    def test_financial_aid_staff_cannot_manage_billing(self):
        Student.objects.create(
            first_name="Role",
            last_name="Fa",
            email="role.fa@example.edu",
            major="Statistics",
            gpa=Decimal("3.20"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        user = User.objects.create_user(username="financialaid", password="Pwd12345!", is_staff=False)
        attach_group(user, GROUP_FINANCIAL_AID)
        client = Client()
        client.force_login(user)
        self.assertEqual(client.get("/charges/").status_code, 403)
        self.assertEqual(client.get("/aid-applications/").status_code, 200)

    def test_auditor_is_read_only(self):
        Student.objects.create(
            first_name="Role",
            last_name="Auditor",
            email="role.audit@example.edu",
            major="Business",
            gpa=Decimal("3.10"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        user = User.objects.create_user(username="auditor", password="Pwd12345!", is_staff=False)
        attach_group(user, GROUP_AUDITOR)
        client = Client()
        client.force_login(user)
        self.assertEqual(client.get("/payments/").status_code, 403)
        self.assertEqual(client.get("/reports/").status_code, 200)
        self.assertEqual(client.get("/audit-log/").status_code, 200)

    def test_auditor_can_download_audit_bundle_zip(self):
        Student.objects.create(
            first_name="Zip",
            last_name="Bundle",
            email="zip.bundle@example.edu",
            major="History",
            gpa=Decimal("3.00"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        user = User.objects.create_user(username="auditor_bundle", password="Pwd12345!", is_staff=False)
        attach_group(user, GROUP_AUDITOR)
        client = Client()
        client.force_login(user)
        response = client.get("/export/audit-bundle/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")

    def test_bursar_denied_audit_bundle_zip(self):
        Student.objects.create(
            first_name="Denied",
            last_name="Zip",
            email="denied.zip@example.edu",
            major="Art",
            gpa=Decimal("3.20"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        user = User.objects.create_user(username="bursar_no_zip", password="Pwd12345!", is_staff=False)
        attach_group(user, GROUP_BURSAR)
        client = Client()
        client.force_login(user)
        self.assertEqual(client.get("/export/audit-bundle/").status_code, 403)

    def test_student_cannot_open_staff_dashboard(self):
        user = User.objects.create_user(username="student_block", password="Pwd12345!", is_staff=False)
        Student.objects.create(
            user=user,
            first_name="Trial",
            last_name="Student",
            email="trial.student-block@example.edu",
            major="Math",
            gpa=Decimal("3.50"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        client = Client()
        client.force_login(user)
        self.assertRedirects(client.get("/"), "/my-profile/", fetch_redirect_response=False)


class StudentProfileCrudTests(TestCase):
    def test_student_can_edit_self_service_details_but_not_official_fields(self):
        user = User.objects.create_user(username="profile_student", password="Pwd12345!")
        student = Student.objects.create(
            user=user,
            first_name="Self",
            last_name="Editor",
            email="self.editor@example.edu",
            major="Accounting",
            gpa=Decimal("3.10"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        client = Client()
        client.force_login(user)

        response = client.post(
            "/my-profile/edit/",
            {
                "preferred_name": "Preferred",
                "phone": "815-555-0100",
                "mailing_address": "DeKalb, IL",
                "emergency_contact_name": "Family Contact",
                "emergency_contact_phone": "815-555-0111",
                "gpa": "4.00",
            },
        )

        self.assertRedirects(response, "/my-profile/", fetch_redirect_response=False)
        student.refresh_from_db()
        details = student.profile_details
        self.assertEqual(student.gpa, Decimal("3.10"))
        self.assertEqual(details.preferred_name, "Preferred")
        self.assertEqual(details.phone, "815-555-0100")

    def test_staff_can_create_student_profile_with_details(self):
        staff = User.objects.create_user(username="profile_staff", password="Pwd12345!", is_staff=True)
        attach_group(staff, GROUP_SUPERVISOR)
        client = Client()
        client.force_login(staff)

        response = client.post(
            "/students/new/",
            {
                "first_name": "New",
                "last_name": "Student",
                "email": "new.student@example.edu",
                "major": "Computer Science",
                "gpa": "3.40",
                "enrollment_status": Student.EnrollmentStatus.FULL_TIME,
                "preferred_name": "New",
                "phone": "815-555-0123",
                "mailing_address": "DeKalb, IL",
                "emergency_contact_name": "Guardian",
                "emergency_contact_phone": "815-555-0133",
                "advisor_name": "Dr. Advisor",
                "class_level": StudentProfileDetails.ClassLevel.JUNIOR,
                "expected_graduation_term": "Spring 2027",
            },
        )

        student = Student.objects.get(email="new.student@example.edu")
        self.assertRedirects(response, f"/students/{student.student_id}/", fetch_redirect_response=False)
        self.assertEqual(student.profile_details.advisor_name, "Dr. Advisor")

    @override_settings(MEDIA_ROOT="/tmp/usfmae_test_media")
    def test_student_upload_download_and_cross_student_denial(self):
        user_one = User.objects.create_user(username="doc_student_one", password="Pwd12345!")
        user_two = User.objects.create_user(username="doc_student_two", password="Pwd12345!")
        student_one = Student.objects.create(
            user=user_one,
            first_name="Doc",
            last_name="Owner",
            email="doc.owner@example.edu",
            major="Finance",
            gpa=Decimal("3.00"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        Student.objects.create(
            user=user_two,
            first_name="Doc",
            last_name="Denied",
            email="doc.denied@example.edu",
            major="Finance",
            gpa=Decimal("3.00"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        client = Client()
        client.force_login(user_one)
        upload = SimpleUploadedFile("aid.pdf", b"%PDF-1.4 test", content_type="application/pdf")

        response = client.post(
            f"/students/{student_one.student_id}/documents/upload/",
            {
                "document_name": "Aid confirmation",
                "document_type": StudentUploadedDocument.DocumentType.FINANCIAL_AID,
                "file": upload,
                "notes": "Test upload",
            },
        )
        self.assertRedirects(response, f"/students/{student_one.student_id}/", fetch_redirect_response=False)
        document = StudentUploadedDocument.objects.get(student=student_one)
        self.assertEqual(client.get(f"/student-documents/{document.id}/download/").status_code, 200)

        client.force_login(user_two)
        self.assertEqual(client.get(f"/student-documents/{document.id}/download/").status_code, 403)

    @override_settings(MEDIA_ROOT="/tmp/usfmae_test_media")
    def test_upload_rejects_unsupported_file_type(self):
        user = User.objects.create_user(username="bad_upload_student", password="Pwd12345!")
        student = Student.objects.create(
            user=user,
            first_name="Bad",
            last_name="Upload",
            email="bad.upload@example.edu",
            major="Finance",
            gpa=Decimal("3.00"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        client = Client()
        client.force_login(user)
        upload = SimpleUploadedFile("malware.exe", b"nope", content_type="application/octet-stream")

        response = client.post(
            f"/students/{student.student_id}/documents/upload/",
            {
                "document_name": "Bad upload",
                "document_type": StudentUploadedDocument.DocumentType.OTHER,
                "file": upload,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(StudentUploadedDocument.objects.filter(student=student).exists())


class AuditTrailTests(TestCase):
    def test_staff_student_view_logged(self):
        staff = User.objects.create_user(username="audit_staff", password="Pwd12345!", is_staff=True)
        attach_group(staff, GROUP_SUPERVISOR)
        target = Student.objects.create(
            first_name="Observe",
            last_name="Target",
            email="observe.target@example.edu",
            major="Engineering",
            gpa=Decimal("3.50"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        client = Client()
        client.force_login(staff)
        baseline = AuditLog.objects.filter(student=target, action=AuditLog.Action.VIEW).count()
        response = client.get(f"/students/{target.student_id}/")
        self.assertEqual(response.status_code, 200)
        after = AuditLog.objects.filter(student=target, action=AuditLog.Action.VIEW).count()
        self.assertGreater(after, baseline)
        self.assertTrue(AuditLog.objects.filter(actor=staff, student=target).exists())

    def test_writes_create_audit_rows(self):
        student = Student.objects.create(
            first_name="Signal",
            last_name="Row",
            email="audit.signal@example.edu",
            major="Physics",
            gpa=Decimal("3.20"),
            enrollment_status=Student.EnrollmentStatus.FULL_TIME,
        )
        before = AuditLog.objects.count()
        Payment.objects.create(
            student=student,
            payment_date=date(2026, 4, 1),
            amount=Decimal("125.00"),
            method=Payment.Method.CASH,
            receipt_no="AUDIT-REC-001",
        )
        self.assertGreater(AuditLog.objects.count(), before)


class SeedDemoDataTests(TestCase):
    def test_seed_demo_data_is_idempotent_and_adds_nigerian_samples(self):
        call_command("seed_demo_data", verbosity=0)
        call_command("seed_demo_data", verbosity=0)

        self.assertEqual(Student.objects.filter(student_id__gte=10, student_id__lte=109).count(), 100)
        self.assertGreaterEqual(StudentCharge.objects.count(), 100)
        self.assertGreaterEqual(Payment.objects.count(), 50)
        self.assertGreaterEqual(AidApplication.objects.count(), 30)
        self.assertGreaterEqual(ActionItem.objects.count(), 20)
        self.assertGreaterEqual(RequiredDocument.objects.count(), 3)
        self.assertGreaterEqual(ApplicationDocument.objects.count(), 30)
        demo = ImportBatch.objects.filter(source_system="USFMAE_IS_DEMO").first()
        self.assertIsNotNone(demo)
        self.assertTrue(Student.objects.filter(import_batch=demo).exists())


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

        self.assertGreaterEqual(ImportBatch.objects.count(), 1)
        batch = ImportBatch.objects.order_by("-batch_id").first()
        student.refresh_from_db()
        payment.refresh_from_db()
        application.refresh_from_db()
        self.assertEqual(student.import_batch_id, batch.pk)
        self.assertEqual(student.source_system, "Access_CSV")
        charge = StudentCharge.objects.get(student_id=1, fee_id=1)
        self.assertEqual(charge.import_batch_id, batch.pk)
