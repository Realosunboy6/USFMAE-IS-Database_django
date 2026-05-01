from datetime import date
from decimal import Decimal
from random import Random

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from finance.rbac import GROUP_SUPERVISOR, setup_finance_groups

from finance.models import (
    ActionItem,
    Administrator,
    AidApplication,
    ApplicationDocument,
    FeeCategory,
    ImportBatch,
    Payment,
    RequiredDocument,
    Scholarship,
    Student,
    StudentCharge,
)


class Command(BaseCommand):
    help = "Seed the USFMAE-IS database with small demo data for local testing."

    def handle(self, *args, **options):
        staff_user, _ = User.objects.update_or_create(
            username="staff",
            defaults={
                "first_name": "Finance",
                "last_name": "Staff",
                "email": "staff@example.edu",
                "is_staff": True,
                "is_superuser": False,
            },
        )
        staff_user.set_password("StaffPass123!")
        staff_user.save()
        setup_finance_groups()
        staff_user.groups.set([Group.objects.get(name=GROUP_SUPERVISOR)])
        demo_batch = ImportBatch.objects.filter(source_system="USFMAE_IS_DEMO").order_by("pk").first()
        if demo_batch is None:
            demo_batch = ImportBatch.objects.create(
                source_system="USFMAE_IS_DEMO",
                label="USFMAE-IS classroom demo",
                notes="Synthetic records produced by seed_demo_data.",
            )
        demo_track = {
            "import_batch": demo_batch,
            "imported_at": timezone.now(),
            "source_system": "USFMAE_IS_DEMO",
        }

        students = [
            {
                "student_id": 1,
                "first_name": "Amina",
                "last_name": "Johnson",
                "email": "amina.johnson@example.edu",
                "major": "Industrial Engineering",
                "gpa": Decimal("3.65"),
                "enrollment_status": Student.EnrollmentStatus.FULL_TIME,
            },
            {
                "student_id": 2,
                "first_name": "Daniel",
                "last_name": "Okafor",
                "email": "daniel.okafor@example.edu",
                "major": "Computer Science",
                "gpa": Decimal("3.10"),
                "enrollment_status": Student.EnrollmentStatus.FULL_TIME,
            },
            {
                "student_id": 3,
                "first_name": "Maya",
                "last_name": "Smith",
                "email": "maya.smith@example.edu",
                "major": "Business Administration",
                "gpa": Decimal("2.85"),
                "enrollment_status": Student.EnrollmentStatus.PART_TIME,
            },
        ]
        for row in students:
            username = f"student{row['student_id']}"
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            user.set_password("StudentPass123!")
            user.save()
            Student.objects.update_or_create(student_id=row["student_id"], defaults={**row, "user": user, **demo_track})

        admin, _ = Administrator.objects.update_or_create(
            admin_id=1,
            defaults={"first_name": "Ibrahim", "last_name": "Oyeyinka", "role": "Financial Aid Reviewer"},
        )

        tuition, _ = FeeCategory.objects.update_or_create(
            fee_id=1,
            defaults={
                "fee_name": "Tuition",
                "standard_amount": Decimal("4500.00"),
                "semester": "Spring 2026",
            },
        )
        housing, _ = FeeCategory.objects.update_or_create(
            fee_id=2,
            defaults={
                "fee_name": "Housing",
                "standard_amount": Decimal("2200.00"),
                "semester": "Spring 2026",
            },
        )

        merit, _ = Scholarship.objects.update_or_create(
            scholarship_id=1,
            defaults={
                "scholarship_name": "Merit Excellence Scholarship",
                "award_type": Scholarship.AwardType.MERIT,
                "award_amount": Decimal("1500.00"),
                "gpa_requirement": Decimal("3.50"),
                "enrollment_requirement": Student.EnrollmentStatus.FULL_TIME,
            },
        )
        access, _ = Scholarship.objects.update_or_create(
            scholarship_id=2,
            defaults={
                "scholarship_name": "Student Access Grant",
                "award_type": Scholarship.AwardType.NEED,
                "award_amount": Decimal("1000.00"),
                "gpa_requirement": Decimal("2.50"),
                "enrollment_requirement": Student.EnrollmentStatus.PART_TIME,
            },
        )

        fafsa_doc, _ = RequiredDocument.objects.update_or_create(
            document_id=1,
            defaults={
                "document_name": "FAFSA Confirmation",
                "description": "Confirmation that the student completed the financial aid application.",
                "applies_to_award_type": Scholarship.AwardType.NEED,
                "is_active": True,
            },
        )
        income_doc, _ = RequiredDocument.objects.update_or_create(
            document_id=2,
            defaults={
                "document_name": "Income Verification",
                "description": "Income or sponsor documentation used for need-based aid review.",
                "applies_to_award_type": Scholarship.AwardType.NEED,
                "is_active": True,
            },
        )
        transcript_doc, _ = RequiredDocument.objects.update_or_create(
            document_id=3,
            defaults={
                "document_name": "Academic Transcript",
                "description": "Transcript used to verify GPA and academic eligibility.",
                "applies_to_award_type": Scholarship.AwardType.MERIT,
                "is_active": True,
            },
        )

        StudentCharge.objects.update_or_create(
            student_id=1,
            fee=tuition,
            defaults={"amount": Decimal("4500.00"), "due_date": date(2026, 2, 15), **demo_track},
        )
        StudentCharge.objects.update_or_create(
            student_id=1,
            fee=housing,
            defaults={"amount": Decimal("2200.00"), "due_date": date(2026, 2, 15), **demo_track},
        )
        StudentCharge.objects.update_or_create(
            student_id=2,
            fee=tuition,
            defaults={"amount": Decimal("4500.00"), "due_date": date(2026, 2, 15), **demo_track},
        )
        StudentCharge.objects.update_or_create(
            student_id=3,
            fee=tuition,
            defaults={"amount": Decimal("2400.00"), "due_date": date(2026, 2, 15), **demo_track},
        )

        Payment.objects.update_or_create(
            payment_id=1,
            defaults={
                "student_id": 1,
                "payment_date": date(2026, 1, 20),
                "amount": Decimal("3000.00"),
                "method": Payment.Method.CARD,
                "receipt_no": "R-1001",
                **demo_track,
            },
        )
        Payment.objects.update_or_create(
            payment_id=2,
            defaults={
                "student_id": 2,
                "payment_date": date(2026, 1, 25),
                "amount": Decimal("1500.00"),
                "method": Payment.Method.BANK_TRANSFER,
                "receipt_no": "R-1002",
                **demo_track,
            },
        )

        application_one, _ = AidApplication.objects.update_or_create(
            application_id=1,
            defaults={
                "student_id": 1,
                "scholarship": merit,
                "administrator": admin,
                "application_date": date(2026, 1, 18),
                "docs_submitted": True,
                "status": AidApplication.Status.PENDING,
                **demo_track,
            },
        )
        application_two, _ = AidApplication.objects.update_or_create(
            application_id=2,
            defaults={
                "student_id": 3,
                "scholarship": access,
                "administrator": admin,
                "application_date": date(2026, 1, 22),
                "docs_submitted": False,
                "status": AidApplication.Status.NEEDS_DOCUMENTS,
                **demo_track,
            },
        )

        ApplicationDocument.objects.update_or_create(
            application=application_one,
            required_document=transcript_doc,
            defaults={
                "status": ApplicationDocument.Status.ACCEPTED,
                "received_date": date(2026, 1, 18),
                "notes": "Transcript confirms GPA requirement.",
                **demo_track,
            },
        )
        ApplicationDocument.objects.update_or_create(
            application=application_two,
            required_document=fafsa_doc,
            defaults={
                "status": ApplicationDocument.Status.REQUIRED,
                "received_date": None,
                "notes": "Student still needs to upload aid confirmation.",
                **demo_track,
            },
        )

        ActionItem.objects.update_or_create(
            action_id=1,
            defaults={
                "student_id": 1,
                "title": "Review remaining spring balance",
                "description": "Student has charges and should confirm payment plan or additional aid.",
                "category": ActionItem.Category.BALANCE,
                "priority": ActionItem.Priority.NORMAL,
                "due_date": date(2026, 2, 10),
                "status": ActionItem.Status.OPEN,
                **demo_track,
            },
        )
        ActionItem.objects.update_or_create(
            action_id=2,
            defaults={
                "student_id": 3,
                "title": "Submit missing FAFSA confirmation",
                "description": "Aid review cannot be completed until required documentation is received.",
                "category": ActionItem.Category.DOCUMENT,
                "priority": ActionItem.Priority.URGENT,
                "due_date": date(2026, 1, 30),
                "status": ActionItem.Status.OPEN,
                **demo_track,
            },
        )

        rng = Random(582)
        first_names = [
            "Adebayo",
            "Adaeze",
            "Amaka",
            "Ayomide",
            "Babatunde",
            "Boluwatife",
            "Chiamaka",
            "Chidera",
            "Chinedu",
            "Chioma",
            "Damilola",
            "Emeka",
            "Eniola",
            "Femi",
            "Funmilayo",
            "Ifeanyi",
            "Ifeoma",
            "Ireti",
            "Kehinde",
            "Kelechi",
            "Mobolaji",
            "Ngozi",
            "Nnamdi",
            "Obinna",
            "Ogechi",
            "Oluchi",
            "Oluwatobi",
            "Opeyemi",
            "Sade",
            "Temitope",
            "Adeola",
            "Adetola",
            "Aisha",
            "Aminu",
            "Bisi",
            "Bukola",
            "Chigozie",
            "Chinonso",
            "Ebuka",
            "Esther",
            "Farida",
            "Fatima",
            "Halima",
            "Hassan",
            "Idris",
            "Jamila",
            "Kabiru",
            "Kanyinsola",
            "Kemi",
            "Kolawole",
            "Latifat",
            "Maryam",
            "Musa",
            "Nneka",
            "Nura",
            "Oladayo",
            "Olajide",
            "Olakunle",
            "Olumide",
            "Onyinye",
            "Rukayat",
            "Saheed",
            "Sani",
            "Tayo",
            "Tolani",
            "Uchenna",
            "Usman",
            "Yemi",
            "Yusuf",
            "Zainab",
            "Adanna",
            "Amarachi",
            "Anuoluwapo",
            "Chisom",
            "Chukwudi",
            "Dara",
            "David",
            "Efe",
            "Folake",
            "Gbemisola",
            "Hadiza",
            "Hauwa",
            "Ifedayo",
            "Ikenna",
            "Iyabo",
            "Jide",
            "Kudirat",
            "Lola",
            "Morenikeji",
            "Munachi",
            "Ndidi",
            "Nkem",
            "Obiageli",
            "Olabisi",
            "Oluwafemi",
            "Omolola",
            "Rasheed",
            "Segun",
            "Tunde",
            "Ugochukwu",
            "Yewande",
            "Zubair",
        ]
        last_names = [
            "Abdullahi",
            "Adebisi",
            "Adeyemi",
            "Afolayan",
            "Agbaje",
            "Akande",
            "Akinola",
            "Balogun",
            "Bello",
            "Chukwu",
            "Danjuma",
            "Eze",
            "Falana",
            "Ibrahim",
            "Kalu",
            "Lawal",
            "Nwachukwu",
            "Nwosu",
            "Obi",
            "Okafor",
            "Okeke",
            "Okonkwo",
            "Oladele",
            "Oladipo",
            "Olamide",
            "Oluwaseun",
            "Onyeka",
            "Osagie",
            "Suleiman",
            "Yakubu",
            "Abiola",
            "Adeleke",
            "Adesina",
            "Akinyemi",
            "Alabi",
            "Amaechi",
            "Anyanwu",
            "Bakare",
            "Bamidele",
            "Bassey",
            "Dauda",
            "Ekwueme",
            "Esangbedo",
            "Garba",
            "Giwa",
            "Hassan",
            "Ibe",
            "Iheanacho",
            "Iwu",
            "Jibril",
            "Kachalla",
            "Ladipo",
            "Maduka",
            "Mohammed",
            "Musa",
            "Ndukwe",
            "Nnamani",
            "Nwankwo",
            "Obasanjo",
            "Odili",
            "Ojo",
            "Okoro",
            "Olaniyan",
            "Omotoso",
            "Onuorah",
            "Orji",
            "Owolabi",
            "Salami",
            "Sani",
            "Tijani",
            "Umar",
            "Usman",
            "Yusuf",
            "Zakari",
            "Abubakar",
            "Adamu",
            "Ajayi",
            "Akintoye",
            "Anosike",
            "Chukwuma",
            "Egbuna",
            "Ekong",
            "Fashola",
            "Gbadamosi",
            "Iroegbu",
            "Ismaila",
            "Jega",
            "Kolawole",
            "Maigari",
            "Njoku",
            "Nwafor",
            "Obinna",
            "Odukoya",
            "Ogbemudia",
            "Okorie",
            "Olowu",
            "Onabanjo",
            "Oyedepo",
            "Shagari",
            "Tambuwal",
            "Uba",
            "Wachuku",
        ]
        majors = [
            "Accounting",
            "Business Administration",
            "Computer Science",
            "Economics",
            "Industrial Engineering",
            "Information Systems",
            "Public Administration",
            "Statistics",
        ]
        statuses = [
            Student.EnrollmentStatus.FULL_TIME,
            Student.EnrollmentStatus.FULL_TIME,
            Student.EnrollmentStatus.PART_TIME,
        ]

        for index in range(100):
            student_id = 10 + index
            first_name = first_names[index]
            last_name = last_names[index]
            email = f"{first_name.lower()}.{last_name.lower()}{student_id}@example.edu"
            user, _ = User.objects.update_or_create(
                username=f"student{student_id}",
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "is_staff": False,
                    "is_superuser": False,
                },
            )
            user.set_password("StudentPass123!")
            user.save()
            student, _ = Student.objects.update_or_create(
                student_id=student_id,
                defaults={
                    "user": user,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "major": majors[index % len(majors)],
                    "gpa": Decimal(f"{rng.uniform(2.10, 4.00):.2f}"),
                    "enrollment_status": statuses[index % len(statuses)],
                    **demo_track,
                },
            )

            tuition_amount = Decimal("4500.00") if student.enrollment_status == Student.EnrollmentStatus.FULL_TIME else Decimal("2400.00")
            StudentCharge.objects.update_or_create(
                student=student,
                fee=tuition,
                defaults={"amount": tuition_amount, "due_date": date(2026, 2, 15), **demo_track},
            )

            if index % 4 == 0:
                StudentCharge.objects.update_or_create(
                    student=student,
                    fee=housing,
                    defaults={"amount": Decimal("2200.00"), "due_date": date(2026, 2, 15), **demo_track},
                )

            if index % 2 == 0:
                Payment.objects.update_or_create(
                    payment_id=1000 + index,
                    defaults={
                        "student": student,
                        "payment_date": date(2026, 1, 10 + (index % 18)),
                        "amount": Decimal("1500.00") + Decimal(index % 5) * Decimal("250.00"),
                        "method": Payment.Method.BANK_TRANSFER if index % 3 == 0 else Payment.Method.CARD,
                        "receipt_no": f"R-NG-{student_id:03d}",
                        **demo_track,
                    },
                )

            if index % 3 == 0:
                scholarship = merit if index % 2 == 0 else access
                application, _ = AidApplication.objects.update_or_create(
                    application_id=2000 + index,
                    defaults={
                        "student": student,
                        "scholarship": scholarship,
                        "administrator": admin,
                        "application_date": date(2026, 1, 5 + (index % 20)),
                        "docs_submitted": index % 6 != 3,
                        "status": AidApplication.Status.PENDING if index % 6 != 3 else AidApplication.Status.NEEDS_DOCUMENTS,
                        **demo_track,
                    },
                )
                required_document = transcript_doc if scholarship == merit else income_doc
                document_status = (
                    ApplicationDocument.Status.SUBMITTED
                    if index % 6 != 3
                    else ApplicationDocument.Status.REQUIRED
                )
                ApplicationDocument.objects.update_or_create(
                    application=application,
                    required_document=required_document,
                    defaults={
                        "status": document_status,
                        "received_date": date(2026, 1, 6 + (index % 18)) if document_status == ApplicationDocument.Status.SUBMITTED else None,
                        "notes": "Demo document record for aid review.",
                        **demo_track,
                    },
                )

            if index % 5 == 0:
                ActionItem.objects.update_or_create(
                    action_id=1000 + index,
                    defaults={
                        "student": student,
                        "title": "Follow up on student account",
                        "description": "Review balance, payment status, or aid requirements before the deadline.",
                        "category": ActionItem.Category.AID if index % 10 == 0 else ActionItem.Category.BALANCE,
                        "priority": ActionItem.Priority.URGENT if index % 15 == 0 else ActionItem.Priority.NORMAL,
                        "due_date": date(2026, 2, 1 + (index % 20)),
                        "status": ActionItem.Status.OPEN,
                        **demo_track,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
