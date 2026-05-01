import csv
import io
import zipfile
from pathlib import Path
from decimal import Decimal, InvalidOperation
from functools import wraps
from urllib.parse import quote

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import (
    ActionItemForm,
    AidApplicationForm,
    AidReviewForm,
    ApplicationDocumentChecklistForm,
    ApplicationDocumentForm,
    PaymentForm,
    StaffStudentDocumentReviewForm,
    StaffStudentProfileDetailsForm,
    StaffStudentProfileForm,
    StudentCreateForm,
    StudentChargeForm,
    StudentDocumentUploadForm,
    StudentSelfProfileDetailsForm,
)
from .models import (
    ActionItem,
    AidApplication,
    ApplicationDocument,
    AuditLog,
    FeeCategory,
    ImportBatch,
    Payment,
    Student,
    StudentCharge,
    StudentProfileDetails,
    StudentUploadedDocument,
)
from .rbac import FinancePermissions, user_has_finance_perm
from .services import (
    aid_status_report,
    application_document_report,
    balance_report,
    dashboard_metrics,
    hold_risk_report,
    open_action_items,
    overdue_charges,
    payment_summary,
    student_financial_summary,
)


def finance_perm_required(codename):
    def decorator(view_fn):
        @wraps(view_fn)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                encoded = quote(request.get_full_path() or "/", safe="/")
                return redirect(f"/login/?next={encoded}")
            if not user_has_finance_perm(request.user, codename):
                return HttpResponseForbidden("Insufficient finance permissions.")
            return view_fn(request, *args, **kwargs)

        return _wrapped

    return decorator


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def write_profile_audit(request, *, student, action, object_type, object_id="", summary=""):
    AuditLog.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        student=student,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        summary=f"{summary} | ip={client_ip(request)} ua={request.META.get('HTTP_USER_AGENT', '')[:160]}",
    )


def can_view_student(request, student):
    viewer = getattr(request.user, "student_profile", None)
    is_self_service = viewer is not None and viewer.student_id == student.student_id
    directory_access = user_has_finance_perm(request.user, FinancePermissions.VIEW_STUDENT_DIRECTORY)
    return is_self_service or directory_access


def can_staff_manage_profiles(user):
    return user_has_finance_perm(user, FinancePermissions.VIEW_STUDENT_DIRECTORY)


@login_required
def dashboard(request):
    if not user_has_finance_perm(request.user, FinancePermissions.ACCESS_DASHBOARD):
        return redirect("finance:my_profile")
    context = {
        "metrics": dashboard_metrics(),
        "students": Student.objects.all()[:10],
        "recent_payments": Payment.objects.select_related("student")[:5],
        "open_action_items": open_action_items()[:8],
        "pending_applications": AidApplication.objects.select_related("student", "scholarship").filter(
            status=AidApplication.Status.PENDING,
        )[:5],
    }
    return render(request, "finance/dashboard.html", context)


class StudentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Student
    template_name = "finance/student_list.html"
    context_object_name = "students"
    paginate_by = 25

    def test_func(self):
        return user_has_finance_perm(self.request.user, FinancePermissions.VIEW_STUDENT_DIRECTORY)

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
                | Q(major__icontains=query),
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


@login_required
def my_profile(request):
    if user_has_finance_perm(request.user, FinancePermissions.ACCESS_DASHBOARD):
        return redirect("finance:dashboard")

    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return render(request, "finance/no_student_profile.html")

    return render_student_profile(
        request,
        student,
        show_back_to_students=False,
        log_staff_student_access=False,
    )


def snapshot_message(student):
    batch = getattr(student, "import_batch", None)
    if batch is not None:
        label = batch.label.strip() if batch.label else f"batch #{batch.pk}"
        return (
            f"Imported snapshot from {batch.source_system} ({label}). "
            f"Batch recorded {batch.imported_at:%Y-%m-%d %H:%M}. "
            "Totals remain explanatory until reconciled with the official ledger."
        )

    details = []
    if student.source_system:
        details.append(f"labeled upstream source: {student.source_system}")
    if student.imported_at:
        details.append(f"student profile row refreshed {student.imported_at:%Y-%m-%d %H:%M}")
    if details:
        return (
            "Clarity-layer metadata (" + "; ".join(details) + "). "
            "Figures shown here are illustrative relative to registrar/billing statements."
        )
    return (
        "These totals come from this demo clarity dataset—they are illustrative only versus production "
        "student financial systems."
    )


def render_student_profile(request, student, *, show_back_to_students, log_staff_student_access=False):
    student = Student.objects.prefetch_related(
        "aid_applications__documents__required_document",
        "charges__fee",
        "uploaded_documents",
    ).select_related("import_batch").get(pk=student.pk)
    details, _ = StudentProfileDetails.objects.get_or_create(student=student)
    applications = list(student.aid_applications.all())
    if log_staff_student_access:
        AuditLog.objects.create(
            actor=request.user,
            student=student,
            action=AuditLog.Action.VIEW,
            object_type="StudentProfile",
            object_id=str(student.student_id),
            summary=f"Viewed clarity profile for {student}",
        )
    context = {
        "student": student,
        "summary": student_financial_summary(student),
        "charges": student.charges.select_related("fee"),
        "payments": student.payments.all(),
        "applications": applications,
        "action_items": student.action_items.all(),
        "profile_details": details,
        "uploaded_documents": student.uploaded_documents.exclude(status=StudentUploadedDocument.Status.ARCHIVED),
        "show_back_to_students": show_back_to_students,
        "data_snapshot_notice": snapshot_message(student),
    }
    return render(request, "finance/student_detail.html", context)


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    viewer = getattr(request.user, "student_profile", None)
    is_self_service = viewer is not None and viewer.student_id == student.student_id
    directory_access = user_has_finance_perm(request.user, FinancePermissions.VIEW_STUDENT_DIRECTORY)

    if not is_self_service and not directory_access:
        return HttpResponseForbidden("You cannot view another student's financial profile.")

    staff_lookup = directory_access and not is_self_service
    return render_student_profile(
        request,
        student,
        show_back_to_students=directory_access,
        log_staff_student_access=staff_lookup,
    )


@finance_perm_required(FinancePermissions.VIEW_STUDENT_DIRECTORY)
def student_create(request):
    form = StudentCreateForm(request.POST or None)
    details_form = StaffStudentProfileDetailsForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid() and details_form.is_valid():
        student = form.save()
        details = details_form.save(commit=False)
        details.student = student
        details.save()
        write_profile_audit(
            request,
            student=student,
            action=AuditLog.Action.CREATE,
            object_type="StudentProfile",
            object_id=student.student_id,
            summary=f"Created student profile for {student}",
        )
        return redirect("finance:student_detail", student_id=student.student_id)
    return render(
        request,
        "finance/student_profile_form.html",
        {"form": form, "details_form": details_form, "mode": "create", "student": None},
    )


@login_required
def my_profile_edit(request):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        return render(request, "finance/no_student_profile.html")
    details, _ = StudentProfileDetails.objects.get_or_create(student=student)
    form = StudentSelfProfileDetailsForm(request.POST or None, instance=details)
    if request.method == "POST" and form.is_valid():
        form.save()
        write_profile_audit(
            request,
            student=student,
            action=AuditLog.Action.UPDATE,
            object_type="StudentProfileDetails",
            object_id=details.pk,
            summary="Student updated self-service profile fields",
        )
        return redirect("finance:my_profile")
    return render(
        request,
        "finance/student_profile_form.html",
        {"details_form": form, "mode": "self_edit", "student": student},
    )


@finance_perm_required(FinancePermissions.VIEW_STUDENT_DIRECTORY)
def student_edit(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    details, _ = StudentProfileDetails.objects.get_or_create(student=student)
    form = StaffStudentProfileForm(request.POST or None, instance=student)
    details_form = StaffStudentProfileDetailsForm(request.POST or None, request.FILES or None, instance=details)
    if request.method == "POST" and form.is_valid() and details_form.is_valid():
        form.save()
        details_form.save()
        write_profile_audit(
            request,
            student=student,
            action=AuditLog.Action.UPDATE,
            object_type="StudentProfile",
            object_id=student.student_id,
            summary=f"Staff updated student profile for {student}",
        )
        return redirect("finance:student_detail", student_id=student.student_id)
    return render(
        request,
        "finance/student_profile_form.html",
        {"form": form, "details_form": details_form, "mode": "staff_edit", "student": student},
    )


@login_required
def student_document_upload(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if not can_view_student(request, student):
        return HttpResponseForbidden("You cannot upload documents for this student.")
    form = StudentDocumentUploadForm(request.POST or None, request.FILES or None)
    form.fields["application"].queryset = student.aid_applications.select_related("scholarship")
    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.student = student
        document.uploaded_by = request.user
        document.save()
        write_profile_audit(
            request,
            student=student,
            action=AuditLog.Action.CREATE,
            object_type="StudentUploadedDocument",
            object_id=document.pk,
            summary=f"Uploaded document {document.document_name}",
        )
        return redirect("finance:student_detail", student_id=student.student_id)
    return render(request, "finance/student_document_form.html", {"form": form, "student": student, "mode": "upload"})


@login_required
def student_document_download(request, document_id):
    document = get_object_or_404(StudentUploadedDocument, pk=document_id)
    if not can_view_student(request, document.student):
        return HttpResponseForbidden("You cannot download this document.")
    if not document.file:
        raise Http404("Document file is missing.")
    write_profile_audit(
        request,
        student=document.student,
        action=AuditLog.Action.VIEW,
        object_type="StudentUploadedDocument",
        object_id=document.pk,
        summary=f"Downloaded document {document.document_name}",
    )
    path = Path(document.file.path)
    if not path.exists():
        raise Http404("Document file is missing.")
    return FileResponse(path.open("rb"), as_attachment=True, filename=path.name)


@finance_perm_required(FinancePermissions.VIEW_STUDENT_DIRECTORY)
def student_document_review(request, document_id):
    document = get_object_or_404(StudentUploadedDocument, pk=document_id)
    form = StaffStudentDocumentReviewForm(request.POST or None, instance=document)
    if request.method == "POST" and form.is_valid():
        reviewed = form.save(commit=False)
        reviewed.reviewed_at = timezone.now()
        reviewed.save()
        write_profile_audit(
            request,
            student=document.student,
            action=AuditLog.Action.UPDATE,
            object_type="StudentUploadedDocument",
            object_id=document.pk,
            summary=f"Reviewed document {document.document_name}: {document.get_status_display()}",
        )
        return redirect("finance:student_detail", student_id=document.student_id)
    return render(request, "finance/student_document_form.html", {"form": form, "student": document.student, "document": document, "mode": "review"})


@finance_perm_required(FinancePermissions.VIEW_STUDENT_DIRECTORY)
def student_document_archive(request, document_id):
    document = get_object_or_404(StudentUploadedDocument, pk=document_id)
    if request.method != "POST":
        return HttpResponseForbidden("Archive requires POST.")
    document.status = StudentUploadedDocument.Status.ARCHIVED
    document.archived_at = timezone.now()
    document.save(update_fields=["status", "archived_at"])
    write_profile_audit(
        request,
        student=document.student,
        action=AuditLog.Action.DELETE,
        object_type="StudentUploadedDocument",
        object_id=document.pk,
        summary=f"Archived document {document.document_name}",
    )
    return redirect("finance:student_detail", student_id=document.student_id)


@finance_perm_required(FinancePermissions.MANAGE_BILLING)
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


@finance_perm_required(FinancePermissions.MANAGE_BILLING)
def payments(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("finance:payments")
    return render(request, "finance/payments.html", {"form": form, "payments": payment_summary()})


@finance_perm_required(FinancePermissions.MANAGE_AID)
def aid_applications(request):
    form = AidApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("finance:aid_applications")
    return render(
        request,
        "finance/aid_applications.html",
        {"form": form, "applications": aid_status_report(), "document_report": application_document_report()},
    )


@finance_perm_required(FinancePermissions.MANAGE_AID)
def aid_review(request, application_id):
    application = get_object_or_404(AidApplication, application_id=application_id)
    form = AidReviewForm(instance=application)
    document_form = ApplicationDocumentChecklistForm()
    if request.method == "POST":
        if "save_review" in request.POST:
            form = AidReviewForm(request.POST, instance=application)
            if form.is_valid():
                form.save()
                return redirect("finance:aid_applications")
        elif "save_document" in request.POST:
            document_form = ApplicationDocumentChecklistForm(request.POST)
            if document_form.is_valid():
                document = document_form.save(commit=False)
                document.application = application
                document.save()
                return redirect("finance:aid_review", application_id=application.application_id)
    return render(
        request,
        "finance/admin_review.html",
        {
            "form": form,
            "document_form": document_form,
            "application": application,
            "documents": application.documents.select_related("required_document"),
        },
    )


@finance_perm_required(FinancePermissions.MANAGE_ACTION_ITEMS)
def action_items(request):
    form = ActionItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("finance:action_items")
    return render(
        request,
        "finance/action_items.html",
        {
            "form": form,
            "action_items": ActionItem.objects.select_related("student").all(),
        },
    )


@finance_perm_required(FinancePermissions.MANAGE_AID)
def application_documents(request):
    form = ApplicationDocumentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("finance:application_documents")
    return render(
        request,
        "finance/application_documents.html",
        {
            "form": form,
            "documents": ApplicationDocument.objects.select_related(
                "application__student",
                "application__scholarship",
                "required_document",
            ),
        },
    )


@finance_perm_required(FinancePermissions.VIEW_REPORTS)
def reports(request):
    semester = (request.GET.get("semester") or "").strip()
    aid_status = (request.GET.get("aid_status") or "").strip()
    only_overdue = request.GET.get("only_overdue") == "1"
    missing_documents = request.GET.get("missing_documents") == "1"

    raw_min_balance = (request.GET.get("min_balance") or "").strip()
    min_balance = None
    if raw_min_balance:
        try:
            min_balance = Decimal(raw_min_balance)
        except InvalidOperation:
            min_balance = None

    context = {
        "balance_report": balance_report(
            min_balance=min_balance,
            only_overdue=only_overdue,
            semester=semester or None,
        ),
        "payment_report": payment_summary(),
        "aid_report": aid_status_report(
            status=aid_status or None,
            missing_documents=missing_documents,
        ),
        "action_items": open_action_items(),
        "document_report": application_document_report(),
        "hold_risk_report": hold_risk_report(),
        "overdue_charges": overdue_charges(),
        "semesters": FeeCategory.objects.values_list("semester", flat=True).distinct().order_by("semester"),
        "aid_statuses": AidApplication.Status.choices,
        "filters": {
            "semester": semester,
            "aid_status": aid_status,
            "only_overdue": only_overdue,
            "missing_documents": missing_documents,
            "min_balance": raw_min_balance,
        },
    }
    return render(request, "finance/reports.html", context)


@finance_perm_required(FinancePermissions.VIEW_AUDIT_LOG)
def audit_log(request):
    entries = AuditLog.objects.select_related("actor", "student").order_by("-created_at")[:500]
    return render(request, "finance/audit_log.html", {"entries": entries})


def _csv_from_queryset(queryset, fieldnames):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in queryset.iterator():
        out = {}
        for key in fieldnames:
            val = row.get(key)
            if val is None:
                out[key] = ""
            elif hasattr(val, "isoformat"):
                out[key] = val.isoformat()
            else:
                out[key] = val
        writer.writerow(out)
    return buffer.getvalue()


@finance_perm_required(FinancePermissions.VIEW_AUDIT_LOG)
def audit_bundle_export(request):
    """ZIP of CSV snapshots for compliance / offline review (read-only extract)."""

    bundles = [
        (
            "students.csv",
            Student.objects.values(
                "student_id",
                "first_name",
                "last_name",
                "email",
                "major",
                "gpa",
                "enrollment_status",
                "source_system",
                "import_batch_id",
                "imported_at",
            ),
            [
                "student_id",
                "first_name",
                "last_name",
                "email",
                "major",
                "gpa",
                "enrollment_status",
                "source_system",
                "import_batch_id",
                "imported_at",
            ],
        ),
        (
            "payments.csv",
            Payment.objects.values(
                "payment_id",
                "student_id",
                "payment_date",
                "amount",
                "method",
                "receipt_no",
                "source_system",
                "import_batch_id",
                "imported_at",
            ),
            [
                "payment_id",
                "student_id",
                "payment_date",
                "amount",
                "method",
                "receipt_no",
                "source_system",
                "import_batch_id",
                "imported_at",
            ],
        ),
        (
            "student_charges.csv",
            StudentCharge.objects.values(
                "id",
                "student_id",
                "fee_id",
                "amount",
                "due_date",
                "source_system",
                "import_batch_id",
                "imported_at",
            ),
            [
                "id",
                "student_id",
                "fee_id",
                "amount",
                "due_date",
                "source_system",
                "import_batch_id",
                "imported_at",
            ],
        ),
        (
            "aid_applications.csv",
            AidApplication.objects.values(
                "application_id",
                "student_id",
                "scholarship_id",
                "administrator_id",
                "application_date",
                "docs_submitted",
                "status",
                "source_system",
                "import_batch_id",
                "imported_at",
            ),
            [
                "application_id",
                "student_id",
                "scholarship_id",
                "administrator_id",
                "application_date",
                "docs_submitted",
                "status",
                "source_system",
                "import_batch_id",
                "imported_at",
            ],
        ),
        (
            "application_documents.csv",
            ApplicationDocument.objects.values(
                "id",
                "application_id",
                "required_document_id",
                "status",
                "received_date",
                "notes",
                "source_system",
                "import_batch_id",
                "imported_at",
            ),
            [
                "id",
                "application_id",
                "required_document_id",
                "status",
                "received_date",
                "notes",
                "source_system",
                "import_batch_id",
                "imported_at",
            ],
        ),
        (
            "audit_log.csv",
            AuditLog.objects.values(
                "id",
                "created_at",
                "actor_id",
                "student_id",
                "action",
                "object_type",
                "object_id",
                "summary",
            ),
            [
                "id",
                "created_at",
                "actor_id",
                "student_id",
                "action",
                "object_type",
                "object_id",
                "summary",
            ],
        ),
        (
            "import_batches.csv",
            ImportBatch.objects.values("batch_id", "label", "source_system", "imported_at", "notes"),
            ["batch_id", "label", "source_system", "imported_at", "notes"],
        ),
    ]

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename, queryset, fields in bundles:
            payload = _csv_from_queryset(queryset, fields)
            archive.writestr(filename, payload)
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = 'attachment; filename="usfmae_audit_bundle.zip"'
    return response
