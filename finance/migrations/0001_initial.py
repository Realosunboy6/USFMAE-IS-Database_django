# Generated for the USFMAE-IS class project scaffold.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Administrator",
            fields=[
                ("admin_id", models.AutoField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("role", models.CharField(max_length=100)),
            ],
            options={
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="FeeCategory",
            fields=[
                ("fee_id", models.AutoField(primary_key=True, serialize=False)),
                ("fee_name", models.CharField(max_length=120)),
                ("standard_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("semester", models.CharField(max_length=40)),
            ],
            options={
                "verbose_name_plural": "fee categories",
                "ordering": ["semester", "fee_name"],
            },
        ),
        migrations.CreateModel(
            name="Scholarship",
            fields=[
                ("scholarship_id", models.AutoField(primary_key=True, serialize=False)),
                ("scholarship_name", models.CharField(max_length=150)),
                (
                    "award_type",
                    models.CharField(
                        choices=[
                            ("MERIT", "Merit"),
                            ("NEED", "Need Based"),
                            ("ATHLETIC", "Athletic"),
                            ("OTHER", "Other"),
                        ],
                        default="MERIT",
                        max_length=20,
                    ),
                ),
                ("award_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("gpa_requirement", models.DecimalField(decimal_places=2, max_digits=3)),
                (
                    "enrollment_requirement",
                    models.CharField(
                        choices=[
                            ("FULL_TIME", "Full Time"),
                            ("PART_TIME", "Part Time"),
                            ("INACTIVE", "Inactive"),
                        ],
                        default="FULL_TIME",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "ordering": ["scholarship_name"],
            },
        ),
        migrations.CreateModel(
            name="Student",
            fields=[
                ("student_id", models.AutoField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name", models.CharField(max_length=100)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("major", models.CharField(max_length=120)),
                ("gpa", models.DecimalField(decimal_places=2, max_digits=3)),
                (
                    "enrollment_status",
                    models.CharField(
                        choices=[
                            ("FULL_TIME", "Full Time"),
                            ("PART_TIME", "Part Time"),
                            ("INACTIVE", "Inactive"),
                        ],
                        default="FULL_TIME",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "ordering": ["last_name", "first_name"],
            },
        ),
        migrations.CreateModel(
            name="AidApplication",
            fields=[
                ("application_id", models.AutoField(primary_key=True, serialize=False)),
                ("application_date", models.DateField()),
                ("docs_submitted", models.BooleanField(default=False)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pending"),
                            ("NEEDS_DOCUMENTS", "Needs Documents"),
                            ("APPROVED", "Approved"),
                            ("DENIED", "Denied"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                (
                    "administrator",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_applications",
                        to="finance.administrator",
                    ),
                ),
                (
                    "scholarship",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="aid_applications",
                        to="finance.scholarship",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="aid_applications",
                        to="finance.student",
                    ),
                ),
            ],
            options={
                "ordering": ["-application_date", "student__last_name"],
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("payment_id", models.AutoField(primary_key=True, serialize=False)),
                ("payment_date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "method",
                    models.CharField(
                        choices=[
                            ("CASH", "Cash"),
                            ("CARD", "Card"),
                            ("BANK_TRANSFER", "Bank Transfer"),
                            ("CHECK", "Check"),
                            ("OTHER", "Other"),
                        ],
                        default="CARD",
                        max_length=20,
                    ),
                ),
                ("receipt_no", models.CharField(max_length=50, unique=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="finance.student",
                    ),
                ),
            ],
            options={
                "ordering": ["-payment_date", "student__last_name"],
            },
        ),
        migrations.CreateModel(
            name="StudentCharge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("due_date", models.DateField()),
                (
                    "fee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="student_charges",
                        to="finance.feecategory",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="charges",
                        to="finance.student",
                    ),
                ),
            ],
            options={
                "ordering": ["due_date", "student__last_name"],
                "constraints": [
                    models.UniqueConstraint(fields=("student", "fee"), name="unique_student_fee_charge"),
                ],
            },
        ),
    ]
