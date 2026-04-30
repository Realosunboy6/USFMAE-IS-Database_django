from datetime import date
from decimal import Decimal
from random import Random

from django.core.management.base import BaseCommand

from finance.models import (
    Administrator,
    AidApplication,
    FeeCategory,
    Payment,
    Scholarship,
    Student,
    StudentCharge,
)


class Command(BaseCommand):
    help = "Seed the USFMAE-IS database with small demo data for local testing."

    def handle(self, *args, **options):
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
            Student.objects.update_or_create(student_id=row["student_id"], defaults=row)

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

        StudentCharge.objects.update_or_create(
            student_id=1,
            fee=tuition,
            defaults={"amount": Decimal("4500.00"), "due_date": date(2026, 2, 15)},
        )
        StudentCharge.objects.update_or_create(
            student_id=1,
            fee=housing,
            defaults={"amount": Decimal("2200.00"), "due_date": date(2026, 2, 15)},
        )
        StudentCharge.objects.update_or_create(
            student_id=2,
            fee=tuition,
            defaults={"amount": Decimal("4500.00"), "due_date": date(2026, 2, 15)},
        )
        StudentCharge.objects.update_or_create(
            student_id=3,
            fee=tuition,
            defaults={"amount": Decimal("2400.00"), "due_date": date(2026, 2, 15)},
        )

        Payment.objects.update_or_create(
            payment_id=1,
            defaults={
                "student_id": 1,
                "payment_date": date(2026, 1, 20),
                "amount": Decimal("3000.00"),
                "method": Payment.Method.CARD,
                "receipt_no": "R-1001",
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
            },
        )

        AidApplication.objects.update_or_create(
            application_id=1,
            defaults={
                "student_id": 1,
                "scholarship": merit,
                "administrator": admin,
                "application_date": date(2026, 1, 18),
                "docs_submitted": True,
                "status": AidApplication.Status.PENDING,
            },
        )
        AidApplication.objects.update_or_create(
            application_id=2,
            defaults={
                "student_id": 3,
                "scholarship": access,
                "administrator": admin,
                "application_date": date(2026, 1, 22),
                "docs_submitted": False,
                "status": AidApplication.Status.NEEDS_DOCUMENTS,
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
            student, _ = Student.objects.update_or_create(
                student_id=student_id,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": f"{first_name.lower()}.{last_name.lower()}{student_id}@example.edu",
                    "major": majors[index % len(majors)],
                    "gpa": Decimal(f"{rng.uniform(2.10, 4.00):.2f}"),
                    "enrollment_status": statuses[index % len(statuses)],
                },
            )

            tuition_amount = Decimal("4500.00") if student.enrollment_status == Student.EnrollmentStatus.FULL_TIME else Decimal("2400.00")
            StudentCharge.objects.update_or_create(
                student=student,
                fee=tuition,
                defaults={"amount": tuition_amount, "due_date": date(2026, 2, 15)},
            )

            if index % 4 == 0:
                StudentCharge.objects.update_or_create(
                    student=student,
                    fee=housing,
                    defaults={"amount": Decimal("2200.00"), "due_date": date(2026, 2, 15)},
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
                    },
                )

            if index % 3 == 0:
                scholarship = merit if index % 2 == 0 else access
                AidApplication.objects.update_or_create(
                    application_id=2000 + index,
                    defaults={
                        "student": student,
                        "scholarship": scholarship,
                        "administrator": admin,
                        "application_date": date(2026, 1, 5 + (index % 20)),
                        "docs_submitted": index % 6 != 3,
                        "status": AidApplication.Status.PENDING if index % 6 != 3 else AidApplication.Status.NEEDS_DOCUMENTS,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
