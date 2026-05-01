from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


app_name = "finance"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("my-profile/", views.my_profile, name="my_profile"),
    path("my-profile/edit/", views.my_profile_edit, name="my_profile_edit"),
    path("students/new/", views.student_create, name="student_create"),
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/<int:student_id>/", views.student_detail, name="student_detail"),
    path("students/<int:student_id>/edit/", views.student_edit, name="student_edit"),
    path("students/<int:student_id>/documents/upload/", views.student_document_upload, name="student_document_upload"),
    path("student-documents/<int:document_id>/download/", views.student_document_download, name="student_document_download"),
    path("student-documents/<int:document_id>/review/", views.student_document_review, name="student_document_review"),
    path("student-documents/<int:document_id>/archive/", views.student_document_archive, name="student_document_archive"),
    path("charges/", views.charges, name="charges"),
    path("payments/", views.payments, name="payments"),
    path("action-items/", views.action_items, name="action_items"),
    path("aid-applications/", views.aid_applications, name="aid_applications"),
    path("aid-documents/", views.application_documents, name="application_documents"),
    path("aid-applications/<int:application_id>/review/", views.aid_review, name="aid_review"),
    path("reports/", views.reports, name="reports"),
    path("audit-log/", views.audit_log, name="audit_log"),
    path("export/audit-bundle/", views.audit_bundle_export, name="audit_bundle_export"),
]
