from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Exists, OuterRef, Q, Sum

from .models import (
    HOLD_RISK_DUE_SOON,
    HOLD_RISK_OVERDUE,
    ActionItem,
    AidApplication,
    ApplicationDocument,
    Payment,
    Student,
    StudentCharge,
)


def money_or_zero(value):
    return value or Decimal("0.00")


def student_financial_summary(student):
    charges = money_or_zero(student.charges.aggregate(total=Sum("amount"))["total"])
    payments = money_or_zero(student.payments.aggregate(total=Sum("amount"))["total"])
    return {
        "student": student,
        "total_charges": charges,
        "total_payments": payments,
        "current_balance": charges - payments,
        "hold_risk_status": student.hold_risk_status,
        "hold_risk_label": student.hold_risk_label,
        "hold_risk_badge": student.hold_risk_badge,
        "hold_risk_message": student.hold_risk_message,
    }


def balance_report(min_balance=None, only_overdue=False, semester=None):
    queryset = Student.objects.all()
    if semester:
        queryset = queryset.filter(charges__fee__semester=semester).distinct()
    rows = [student_financial_summary(student) for student in queryset]
    if min_balance is not None:
        rows = [row for row in rows if row["current_balance"] >= Decimal(str(min_balance))]
    if only_overdue:
        rows = [row for row in rows if row["hold_risk_status"] in {HOLD_RISK_OVERDUE, HOLD_RISK_DUE_SOON}]
    return rows


def hold_risk_report():
    rows = [student_financial_summary(student) for student in Student.objects.all()]
    return [row for row in rows if row["hold_risk_status"] in {HOLD_RISK_OVERDUE, HOLD_RISK_DUE_SOON}]


def overdue_charges():
    today = date.today()
    return StudentCharge.objects.select_related("student", "fee").filter(due_date__lt=today)


def payment_summary():
    return Payment.objects.select_related("student").order_by("-payment_date", "student__last_name")


def applications_missing_documents_queryset():
    has_rows = ApplicationDocument.objects.filter(application_id=OuterRef("pk"))
    blocking = ApplicationDocument.objects.filter(
        application_id=OuterRef("pk"),
        status__in=[
            ApplicationDocument.Status.REQUIRED,
            ApplicationDocument.Status.REJECTED,
        ],
    )
    return AidApplication.objects.annotate(
        _blocking=Exists(blocking),
        _has_rows=Exists(has_rows),
    ).filter(Q(_blocking=True) | (Q(_has_rows=False) & Q(docs_submitted=False)))


def aid_status_report(status=None, missing_documents=False):
    queryset = AidApplication.objects.select_related("student", "scholarship", "administrator")
    if status:
        queryset = queryset.filter(status=status)
    if missing_documents:
        queryset = queryset.filter(
            Exists(
                ApplicationDocument.objects.filter(
                    application_id=OuterRef("pk"),
                    status__in=[
                        ApplicationDocument.Status.REQUIRED,
                        ApplicationDocument.Status.REJECTED,
                    ],
                ),
            )
            | (
                ~Exists(ApplicationDocument.objects.filter(application_id=OuterRef("pk")))
                & Q(docs_submitted=False)
            ),
        )
    return queryset.order_by("status", "-application_date")


def dashboard_metrics():
    charge_total = money_or_zero(StudentCharge.objects.aggregate(total=Sum("amount"))["total"])
    payment_total = money_or_zero(Payment.objects.aggregate(total=Sum("amount"))["total"])
    today = date.today()
    soon = today + timedelta(days=14)
    return {
        "student_count": Student.objects.count(),
        "total_charges": charge_total,
        "total_payments": payment_total,
        "total_balance": charge_total - payment_total,
        "pending_applications": AidApplication.objects.filter(status=AidApplication.Status.PENDING).count(),
        "open_action_items": ActionItem.objects.filter(status=ActionItem.Status.OPEN).count(),
        "missing_documents": applications_missing_documents_queryset().count(),
        "overdue_charges": StudentCharge.objects.filter(due_date__lt=today).count(),
        "due_soon_charges": StudentCharge.objects.filter(due_date__gte=today, due_date__lte=soon).count(),
        "applications_by_status": AidApplication.objects.values("status").annotate(count=Count("status")),
    }


def open_action_items():
    return ActionItem.objects.select_related("student").filter(status=ActionItem.Status.OPEN).order_by(
        "due_date",
        "-priority",
    )


def application_document_report():
    return ApplicationDocument.objects.select_related(
        "application__student",
        "application__scholarship",
        "required_document",
    ).order_by("status", "application__student__last_name")
