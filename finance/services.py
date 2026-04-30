from decimal import Decimal

from django.db.models import Count, Sum

from .models import AidApplication, Payment, Student, StudentCharge


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
    }


def balance_report():
    return [student_financial_summary(student) for student in Student.objects.all()]


def payment_summary():
    return Payment.objects.select_related("student").order_by("-payment_date", "student__last_name")


def aid_status_report():
    return AidApplication.objects.select_related("student", "scholarship", "administrator").order_by(
        "status",
        "-application_date",
    )


def dashboard_metrics():
    charge_total = money_or_zero(StudentCharge.objects.aggregate(total=Sum("amount"))["total"])
    payment_total = money_or_zero(Payment.objects.aggregate(total=Sum("amount"))["total"])
    return {
        "student_count": Student.objects.count(),
        "total_charges": charge_total,
        "total_payments": payment_total,
        "total_balance": charge_total - payment_total,
        "pending_applications": AidApplication.objects.filter(status=AidApplication.Status.PENDING).count(),
        "applications_by_status": AidApplication.objects.values("status").annotate(count=Count("status")),
    }
