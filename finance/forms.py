from django import forms

from .models import AidApplication, Payment, StudentCharge


class AidApplicationForm(forms.ModelForm):
    class Meta:
        model = AidApplication
        fields = ["student", "scholarship", "application_date", "docs_submitted"]
        widgets = {
            "application_date": forms.DateInput(attrs={"type": "date"}),
        }


class AidReviewForm(forms.ModelForm):
    class Meta:
        model = AidApplication
        fields = ["administrator", "docs_submitted", "status"]


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
