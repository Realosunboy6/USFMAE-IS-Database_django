from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.urls import reverse


class Student(models.Model):
    class EnrollmentStatus(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        INACTIVE = "INACTIVE", "Inactive"

    student_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    major = models.CharField(max_length=120)
    gpa = models.DecimalField(max_digits=3, decimal_places=2)
    enrollment_status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.FULL_TIME,
    )

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_absolute_url(self):
        return reverse("finance:student_detail", kwargs={"student_id": self.student_id})

    @property
    def total_charges(self):
        return self.charges.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    @property
    def total_payments(self):
        return self.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    @property
    def current_balance(self):
        return self.total_charges - self.total_payments


class FeeCategory(models.Model):
    fee_id = models.AutoField(primary_key=True)
    fee_name = models.CharField(max_length=120)
    standard_amount = models.DecimalField(max_digits=10, decimal_places=2)
    semester = models.CharField(max_length=40)

    class Meta:
        ordering = ["semester", "fee_name"]
        verbose_name_plural = "fee categories"

    def __str__(self):
        return f"{self.fee_name} ({self.semester})"


class StudentCharge(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="charges")
    fee = models.ForeignKey(FeeCategory, on_delete=models.PROTECT, related_name="student_charges")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

    class Meta:
        ordering = ["due_date", "student__last_name"]
        constraints = [
            models.UniqueConstraint(fields=["student", "fee"], name="unique_student_fee_charge"),
        ]

    def __str__(self):
        return f"{self.student} - {self.fee}: ${self.amount}"


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
        CHECK = "CHECK", "Check"
        OTHER = "OTHER", "Other"

    payment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CARD)
    receipt_no = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["-payment_date", "student__last_name"]

    def __str__(self):
        return f"{self.receipt_no} - {self.student} - ${self.amount}"


class Scholarship(models.Model):
    class AwardType(models.TextChoices):
        MERIT = "MERIT", "Merit"
        NEED = "NEED", "Need Based"
        ATHLETIC = "ATHLETIC", "Athletic"
        OTHER = "OTHER", "Other"

    scholarship_id = models.AutoField(primary_key=True)
    scholarship_name = models.CharField(max_length=150)
    award_type = models.CharField(max_length=20, choices=AwardType.choices, default=AwardType.MERIT)
    award_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gpa_requirement = models.DecimalField(max_digits=3, decimal_places=2)
    enrollment_requirement = models.CharField(
        max_length=20,
        choices=Student.EnrollmentStatus.choices,
        default=Student.EnrollmentStatus.FULL_TIME,
    )

    class Meta:
        ordering = ["scholarship_name"]

    def __str__(self):
        return self.scholarship_name


class Administrator(models.Model):
    admin_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class AidApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        NEEDS_DOCUMENTS = "NEEDS_DOCUMENTS", "Needs Documents"
        APPROVED = "APPROVED", "Approved"
        DENIED = "DENIED", "Denied"

    application_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="aid_applications")
    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.PROTECT,
        related_name="aid_applications",
    )
    administrator = models.ForeignKey(
        Administrator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
    )
    application_date = models.DateField()
    docs_submitted = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ["-application_date", "student__last_name"]

    def __str__(self):
        return f"{self.student} - {self.scholarship} ({self.get_status_display()})"

    @property
    def meets_basic_eligibility(self):
        return (
            self.student.gpa >= self.scholarship.gpa_requirement
            and self.student.enrollment_status == self.scholarship.enrollment_requirement
            and self.docs_submitted
        )
