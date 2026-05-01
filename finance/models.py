from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.urls import reverse


class FinanceDivision(models.Model):
    """Lightweight RBAC anchor for custom Django permissions (rows are optional)."""

    notes = models.TextField(blank=True)

    class Meta:
        default_permissions = ()
        permissions = [
            ("access_dashboard", "Can access staff dashboard"),
            ("view_student_directory", "Can view student directory"),
            ("manage_billing", "Can manage charges and payments"),
            ("manage_aid", "Can manage aid applications"),
            ("manage_action_items", "Can manage action items"),
            ("view_reports", "Can view reports"),
            ("view_audit_log", "Can view audit log"),
            ("full_supervision", "Finance supervisor override"),
            ("system_admin", "Finance system administrator"),
        ]
        verbose_name_plural = "Finance divisions"

    def __str__(self):
        return "Finance divisions"


class ImportBatch(models.Model):
    batch_id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=160, blank=True)
    source_system = models.CharField(max_length=80)
    imported_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-imported_at"]

    def __str__(self):
        return self.label or f"{self.source_system} #{self.pk}"


class AuditLog(models.Model):
    class Action(models.TextChoices):
        VIEW = "VIEW", "View"
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        DIRECTORY = "DIRECTORY", "Directory"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="finance_audit_logs",
    )
    student = models.ForeignKey(
        "Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="finance_audit_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    object_type = models.CharField(max_length=120)
    object_id = models.CharField(max_length=80, blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} {self.object_type}@{self.created_at.isoformat(timespec='seconds')}"


HOLD_RISK_NONE = "NONE"
HOLD_RISK_BALANCE = "BALANCE"
HOLD_RISK_DUE_SOON = "DUE_SOON"
HOLD_RISK_OVERDUE = "OVERDUE"

HOLD_RISK_LABELS = {
    HOLD_RISK_NONE: "No Hold Risk",
    HOLD_RISK_BALANCE: "Balance Due",
    HOLD_RISK_DUE_SOON: "Due Soon",
    HOLD_RISK_OVERDUE: "Overdue",
}

HOLD_RISK_BADGE = {
    HOLD_RISK_NONE: "badge-success",
    HOLD_RISK_BALANCE: "badge-neutral",
    HOLD_RISK_DUE_SOON: "badge-warning",
    HOLD_RISK_OVERDUE: "badge-danger",
}

HOLD_RISK_MESSAGE = {
    HOLD_RISK_NONE: "Your account is in good standing.",
    HOLD_RISK_BALANCE: "You have a balance, but no charge is due soon.",
    HOLD_RISK_DUE_SOON: "A charge is due within 14 days. Plan to pay or set up a payment plan.",
    HOLD_RISK_OVERDUE: "You have an overdue balance. This may delay registration. Please contact Student Financial Services.",
}


class Student(models.Model):
    class EnrollmentStatus(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full Time"
        PART_TIME = "PART_TIME", "Part Time"
        INACTIVE = "INACTIVE", "Inactive"

    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
    )
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
    source_system = models.CharField(max_length=80, blank=True)
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    imported_at = models.DateTimeField(null=True, blank=True)

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

    @property
    def hold_risk_status(self):
        balance = self.current_balance
        if balance <= Decimal("0.00"):
            return HOLD_RISK_NONE
        today = date.today()
        soon_window = today + timedelta(days=14)
        if self.charges.filter(due_date__lt=today).exists():
            return HOLD_RISK_OVERDUE
        if self.charges.filter(due_date__lte=soon_window).exists():
            return HOLD_RISK_DUE_SOON
        return HOLD_RISK_BALANCE

    @property
    def hold_risk_label(self):
        return HOLD_RISK_LABELS[self.hold_risk_status]

    @property
    def hold_risk_badge(self):
        return HOLD_RISK_BADGE[self.hold_risk_status]

    @property
    def hold_risk_message(self):
        return HOLD_RISK_MESSAGE[self.hold_risk_status]


def student_photo_upload_path(instance, filename):
    return f"student_profiles/{instance.student_id}/photo/{filename}"


def student_document_upload_path(instance, filename):
    return f"student_profiles/{instance.student_id}/documents/{filename}"


class StudentProfileDetails(models.Model):
    class ClassLevel(models.TextChoices):
        FRESHMAN = "FRESHMAN", "Freshman"
        SOPHOMORE = "SOPHOMORE", "Sophomore"
        JUNIOR = "JUNIOR", "Junior"
        SENIOR = "SENIOR", "Senior"
        GRADUATE = "GRADUATE", "Graduate"
        OTHER = "OTHER", "Other"

    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="profile_details")
    preferred_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    mailing_address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)
    advisor_name = models.CharField(max_length=120, blank=True)
    class_level = models.CharField(max_length=20, choices=ClassLevel.choices, blank=True)
    expected_graduation_term = models.CharField(max_length=40, blank=True)
    profile_photo = models.FileField(upload_to=student_photo_upload_path, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "student profile details"

    def __str__(self):
        return f"Profile details for {self.student}"


class StudentUploadedDocument(models.Model):
    class DocumentType(models.TextChoices):
        ID = "ID", "ID Card"
        TRANSCRIPT = "TRANSCRIPT", "Transcript"
        FINANCIAL_AID = "FINANCIAL_AID", "Financial Aid"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        ARCHIVED = "ARCHIVED", "Archived"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="uploaded_documents")
    application = models.ForeignKey(
        "AidApplication",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
    )
    document_name = models.CharField(max_length=140)
    document_type = models.CharField(max_length=30, choices=DocumentType.choices, default=DocumentType.OTHER)
    file = models.FileField(upload_to=student_document_upload_path)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_document_uploads",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.student} - {self.document_name}"


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
    source_system = models.CharField(max_length=80, blank=True)
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="charges",
    )
    imported_at = models.DateTimeField(null=True, blank=True)

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
    source_system = models.CharField(max_length=80, blank=True)
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    imported_at = models.DateTimeField(null=True, blank=True)

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
    source_system = models.CharField(max_length=80, blank=True)
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="aid_applications",
    )
    imported_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-application_date", "student__last_name"]

    def __str__(self):
        return f"{self.student} - {self.scholarship} ({self.get_status_display()})"

    def blocking_documents_exist(self):
        return self.documents.filter(status__in=["REQUIRED", "REJECTED"]).exists()

    def documents_satisfied_from_records(self):
        if self.documents.exists():
            return not self.blocking_documents_exist()
        return self.docs_submitted

    def sync_documents_submitted_flag(self):
        desired = self.documents_satisfied_from_records()
        if self.docs_submitted != desired:
            AidApplication.objects.filter(pk=self.pk).update(docs_submitted=desired)
            self.docs_submitted = desired

    @property
    def meets_basic_eligibility(self):
        return all(rule["passed"] for rule in self.eligibility_rules)

    @property
    def eligibility_rules(self):
        docs_ok = self.documents_satisfied_from_records()
        if self.documents.exists():
            missing = self.documents.filter(status__in=["REQUIRED", "REJECTED"]).count()
            docs_actual = f"{missing} open item(s) on checklist" if missing else "Checklist satisfied"
        else:
            docs_actual = "Submitted" if self.docs_submitted else "Missing (legacy flag)"
        return [
            {
                "label": "GPA requirement",
                "expected": str(self.scholarship.gpa_requirement),
                "actual": str(self.student.gpa),
                "passed": self.student.gpa >= self.scholarship.gpa_requirement,
            },
            {
                "label": "Enrollment requirement",
                "expected": self.scholarship.get_enrollment_requirement_display(),
                "actual": self.student.get_enrollment_status_display(),
                "passed": self.student.enrollment_status == self.scholarship.enrollment_requirement,
            },
            {
                "label": "Aid documents checklist",
                "expected": "No required or rejected items outstanding",
                "actual": docs_actual,
                "passed": docs_ok,
            },
        ]

    @property
    def status_timeline(self):
        order = [
            self.Status.PENDING,
            self.Status.NEEDS_DOCUMENTS,
            self.Status.APPROVED,
            self.Status.DENIED,
        ]
        labels = {
            self.Status.PENDING: "Submitted / Pending",
            self.Status.NEEDS_DOCUMENTS: "Needs Documents",
            self.Status.APPROVED: "Approved",
            self.Status.DENIED: "Decision Recorded",
        }
        current_index = order.index(self.status) if self.status in order else 0
        timeline = []
        for index, stage in enumerate(order):
            timeline.append(
                {
                    "key": stage,
                    "label": labels[stage],
                    "current": index == current_index,
                    "completed": index < current_index,
                }
            )
        return timeline


class ActionItem(models.Model):
    class Category(models.TextChoices):
        BALANCE = "BALANCE", "Balance"
        DOCUMENT = "DOCUMENT", "Document"
        PAYMENT = "PAYMENT", "Payment"
        AID = "AID", "Aid"
        GENERAL = "GENERAL", "General"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        NORMAL = "NORMAL", "Normal"
        URGENT = "URGENT", "Urgent"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        COMPLETED = "COMPLETED", "Completed"
        WAIVED = "WAIVED", "Waived"

    action_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="action_items")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    source_system = models.CharField(max_length=80, blank=True)
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_items",
    )
    imported_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["status", "due_date", "-priority", "student__last_name"]

    def __str__(self):
        return f"{self.student} - {self.title}"


class RequiredDocument(models.Model):
    document_id = models.AutoField(primary_key=True)
    document_name = models.CharField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    applies_to_award_type = models.CharField(
        max_length=20,
        choices=Scholarship.AwardType.choices,
        blank=True,
        help_text="Leave blank when the document can apply to any award type.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["document_name"]

    def __str__(self):
        return self.document_name


class ApplicationDocument(models.Model):
    class Status(models.TextChoices):
        REQUIRED = "REQUIRED", "Required"
        SUBMITTED = "SUBMITTED", "Submitted"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        WAIVED = "WAIVED", "Waived"

    application = models.ForeignKey(AidApplication, on_delete=models.CASCADE, related_name="documents")
    required_document = models.ForeignKey(
        RequiredDocument,
        on_delete=models.PROTECT,
        related_name="application_documents",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUIRED)
    received_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    source_system = models.CharField(max_length=80, blank=True)
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="application_documents",
    )
    imported_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["application__student__last_name", "required_document__document_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["application", "required_document"],
                name="unique_application_required_document",
            ),
        ]

    def __str__(self):
        return f"{self.application} - {self.required_document}"
