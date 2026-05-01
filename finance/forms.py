from django import forms
from pathlib import Path

from .models import (
    ActionItem,
    AidApplication,
    ApplicationDocument,
    Payment,
    Student,
    StudentCharge,
    StudentProfileDetails,
    StudentUploadedDocument,
)


MAX_UPLOAD_SIZE = 5 * 1024 * 1024
DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
PHOTO_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def validate_uploaded_file(uploaded_file, *, allowed_extensions, label):
    ext = Path(uploaded_file.name).suffix.lower()
    if ext not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise forms.ValidationError(f"{label} must use one of these file types: {allowed}.")
    if uploaded_file.size > MAX_UPLOAD_SIZE:
        raise forms.ValidationError(f"{label} must be 5MB or smaller.")
    return uploaded_file


class StudentCreateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["user", "first_name", "last_name", "email", "major", "gpa", "enrollment_status"]


class StaffStudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["user", "first_name", "last_name", "email", "major", "gpa", "enrollment_status"]


class StudentSelfProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = StudentProfileDetails
        fields = [
            "preferred_name",
            "phone",
            "mailing_address",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]


class StaffStudentProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = StudentProfileDetails
        fields = [
            "preferred_name",
            "phone",
            "mailing_address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "advisor_name",
            "class_level",
            "expected_graduation_term",
            "profile_photo",
        ]

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if photo:
            validate_uploaded_file(photo, allowed_extensions=PHOTO_EXTENSIONS, label="Profile photo")
        return photo


class StudentDocumentUploadForm(forms.ModelForm):
    class Meta:
        model = StudentUploadedDocument
        fields = ["application", "document_name", "document_type", "file", "notes"]

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        return validate_uploaded_file(uploaded_file, allowed_extensions=DOCUMENT_EXTENSIONS, label="Document")


class StaffStudentDocumentReviewForm(forms.ModelForm):
    class Meta:
        model = StudentUploadedDocument
        fields = ["status", "notes"]


class AidApplicationForm(forms.ModelForm):
    class Meta:
        model = AidApplication
        fields = ["student", "scholarship", "application_date", "docs_submitted"]
        help_texts = {
            "docs_submitted": (
                "Optional legacy checkbox. Detailed ApplicationDocument statuses override this when checklist rows "
                "exist."
            ),
        }
        widgets = {
            "application_date": forms.DateInput(attrs={"type": "date"}),
        }


class AidReviewForm(forms.ModelForm):
    class Meta:
        model = AidApplication
        fields = ["administrator", "docs_submitted", "status"]


class ApplicationDocumentForm(forms.ModelForm):
    class Meta:
        model = ApplicationDocument
        fields = ["application", "required_document", "status", "received_date", "notes"]
        widgets = {
            "received_date": forms.DateInput(attrs={"type": "date"}),
        }


class ApplicationDocumentChecklistForm(forms.ModelForm):
    class Meta:
        model = ApplicationDocument
        fields = ["required_document", "status", "received_date", "notes"]
        widgets = {
            "received_date": forms.DateInput(attrs={"type": "date"}),
        }


class ActionItemForm(forms.ModelForm):
    class Meta:
        model = ActionItem
        fields = ["student", "title", "description", "category", "priority", "due_date", "status"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["student", "payment_date", "amount", "method", "receipt_no"]
        widgets = {
            "payment_date": forms.DateInput(attrs={"type": "date"}),
        }


class StudentChargeForm(forms.ModelForm):
    class Meta:
        model = StudentCharge
        fields = ["student", "fee", "amount", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
