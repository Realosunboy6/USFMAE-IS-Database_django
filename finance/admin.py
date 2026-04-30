from django.contrib import admin

from .models import (
    Administrator,
    AidApplication,
    FeeCategory,
    Payment,
    Scholarship,
    Student,
    StudentCharge,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "last_name", "first_name", "email", "major", "gpa", "enrollment_status")
    search_fields = ("first_name", "last_name", "email", "major")
    list_filter = ("enrollment_status", "major")


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
