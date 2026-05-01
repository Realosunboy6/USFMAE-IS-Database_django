from django.contrib import admin

from .models import (
    ActionItem,
    Administrator,
    AidApplication,
    ApplicationDocument,
    AuditLog,
    FeeCategory,
    FinanceDivision,
    ImportBatch,
    Payment,
    RequiredDocument,
    Scholarship,
    Student,
    StudentCharge,
    StudentProfileDetails,
    StudentUploadedDocument,
)


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("batch_id", "source_system", "label", "imported_at")
    search_fields = ("label", "source_system", "notes")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "object_type", "object_id", "student")
    search_fields = ("summary", "object_type", "object_id")
    list_filter = ("action",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FinanceDivision)
class FinanceDivisionAdmin(admin.ModelAdmin):
    list_display = ("id", "notes")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "last_name", "first_name", "email", "major", "gpa", "enrollment_status")
    search_fields = ("first_name", "last_name", "email", "major")
    list_filter = ("enrollment_status", "major")


@admin.register(StudentProfileDetails)
class StudentProfileDetailsAdmin(admin.ModelAdmin):
    list_display = ("student", "preferred_name", "phone", "class_level", "expected_graduation_term", "updated_at")
    search_fields = ("student__first_name", "student__last_name", "preferred_name", "advisor_name")
    list_filter = ("class_level",)


@admin.register(StudentUploadedDocument)
class StudentUploadedDocumentAdmin(admin.ModelAdmin):
    list_display = ("student", "document_name", "document_type", "status", "uploaded_at", "uploaded_by")
    search_fields = ("student__first_name", "student__last_name", "document_name", "notes")
    list_filter = ("document_type", "status", "uploaded_at")


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ("fee_id", "fee_name", "standard_amount", "semester")
    search_fields = ("fee_name", "semester")
    list_filter = ("semester",)


@admin.register(StudentCharge)
class StudentChargeAdmin(admin.ModelAdmin):
    list_display = ("student", "fee", "amount", "due_date")
    search_fields = ("student__first_name", "student__last_name", "fee__fee_name")
    list_filter = ("due_date", "fee__semester")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "student", "payment_date", "amount", "method", "receipt_no")
    search_fields = ("student__first_name", "student__last_name", "receipt_no")
    list_filter = ("method", "payment_date")


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = (
        "scholarship_id",
        "scholarship_name",
        "award_type",
        "award_amount",
        "gpa_requirement",
        "enrollment_requirement",
    )
    search_fields = ("scholarship_name",)
    list_filter = ("award_type", "enrollment_requirement")


@admin.register(Administrator)
class AdministratorAdmin(admin.ModelAdmin):
    list_display = ("admin_id", "last_name", "first_name", "role")
    search_fields = ("first_name", "last_name", "role")


@admin.register(AidApplication)
class AidApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "application_id",
        "student",
        "scholarship",
        "application_date",
        "docs_submitted",
        "status",
        "administrator",
        "meets_basic_eligibility",
    )
    search_fields = ("student__first_name", "student__last_name", "scholarship__scholarship_name")
    list_filter = ("status", "docs_submitted", "application_date")


@admin.register(ActionItem)
class ActionItemAdmin(admin.ModelAdmin):
    list_display = ("action_id", "student", "title", "category", "priority", "due_date", "status")
    search_fields = ("student__first_name", "student__last_name", "title", "description")
    list_filter = ("category", "priority", "status", "due_date")


@admin.register(RequiredDocument)
class RequiredDocumentAdmin(admin.ModelAdmin):
    list_display = ("document_id", "document_name", "applies_to_award_type", "is_active")
    search_fields = ("document_name", "description")
    list_filter = ("applies_to_award_type", "is_active")


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ("application", "required_document", "status", "received_date")
    search_fields = (
        "application__student__first_name",
        "application__student__last_name",
        "required_document__document_name",
    )
    list_filter = ("status", "received_date", "required_document")
