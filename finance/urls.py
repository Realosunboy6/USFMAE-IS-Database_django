from django.urls import path

from . import views


app_name = "finance"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("students/", views.StudentListView.as_view(), name="student_list"),
    path("students/<int:student_id>/", views.student_detail, name="student_detail"),
    path("charges/", views.charges, name="charges"),
    path("payments/", views.payments, name="payments"),
    path("aid-applications/", views.aid_applications, name="aid_applications"),
    path("aid-applications/<int:application_id>/review/", views.aid_review, name="aid_review"),
    path("reports/", views.reports, name="reports"),
]
