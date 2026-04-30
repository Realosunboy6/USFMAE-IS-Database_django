from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import AidApplicationForm, AidReviewForm, PaymentForm, StudentChargeForm
from .models import AidApplication, Payment, Student, StudentCharge
from .services import aid_status_report, balance_report, dashboard_metrics, payment_summary, student_financial_summary


def dashboard(request):
    context = {
        "metrics": dashboard_metrics(),
        "students": Student.objects.all()[:10],
        "recent_payments": Payment.objects.select_related("student")[:5],
        "pending_applications": AidApplication.objects.select_related("student", "scholarship").filter(
            status=AidApplication.Status.PENDING,
        )[:5],
    }
    return render(request, "finance/dashboard.html", context)


class StudentListView(ListView):
    model = Student
    template_name = "finance/student_list.html"
    context_object_name = "students"


def student_detail(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    return render(
        request,
        "finance/student_detail.html",
        {
            "student": student,
            "summary": student_financial_summary(student),
            "charges": student.charges.select_related("fee"),
            "payments": student.payments.all(),
            "applications": student.aid_applications.select_related("scholarship", "administrator"),
        },
    )


def charges(request):
    form = StudentChargeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("finance:charges")
    return render(
        request,
        "finance/charges.html",
        {"form": form, "charges": StudentCharge.objects.select_related("student", "fee")},
    )


def payments(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("finance:payments")
    return render(request, "finance/payments.html", {"form": form, "payments": payment_summary()})


def aid_applications(request):
    form = AidApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("finance:aid_applications")
    return render(
        request,
        "finance/aid_applications.html",
        {"form": form, "applications": aid_status_report()},
    )


def aid_review(request, application_id):
    application = get_object_or_404(AidApplication, application_id=application_id)
    form = AidReviewForm(request.POST or None, instance=application)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("finance:aid_applications")
    return render(request, "finance/admin_review.html", {"form": form, "application": application})


def reports(request):
    context = {
        "balance_report": balance_report(),
        "payment_report": payment_summary(),
        "aid_report": aid_status_report(),
    }
    return render(request, "finance/reports.html", context)
