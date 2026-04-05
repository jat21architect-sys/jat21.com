import time

from django import forms
from django.conf import settings
from django.core import signing

from .models import ContactInquiry

PROJECT_TYPE_CHOICES = [
    ("", "Select project type…"),
    ("Housing", "Housing"),
    ("Civic", "Civic"),
    ("Workplace", "Workplace"),
    ("Renovation / Adaptive Reuse", "Renovation / Adaptive Reuse"),
    ("Other", "Other"),
]

LEGACY_PROJECT_TYPE_MAP = {
    "Residential Design": "Housing",
    "Commercial Design": "Workplace",
    "Interior Architecture": "Other",
    "Concept Development": "Other",
    "3D Visualisation": "Other",
    "Planning & Consultation": "Other",
    "Renovation / Adaptive Reuse": "Renovation / Adaptive Reuse",
}

BUDGET_CHOICES = [
    ("", "Budget range (optional)…"),
    ("Under 100k", "Under 100k"),
    ("100k – 500k", "100k – 500k"),
    ("500k – 1M", "500k – 1M"),
    ("1M – 5M", "1M – 5M"),
    ("5M+", "5M+"),
    ("To discuss", "To discuss"),
]

TIMELINE_CHOICES = [
    ("", "Timeline (optional)…"),
    ("Immediate", "Immediate"),
    ("1–3 months", "1–3 months"),
    ("3–6 months", "3–6 months"),
    ("6–12 months", "6–12 months"),
    ("1–2 years", "1–2 years"),
    ("Long-term / ongoing", "Long-term / ongoing"),
]

INVALID_SUBMISSION_MESSAGE = "This form expired or became invalid. Reload the page and try again."


class ContactForm(forms.ModelForm):
    project_type = forms.ChoiceField(choices=PROJECT_TYPE_CHOICES, required=False)
    budget_range = forms.ChoiceField(choices=BUDGET_CHOICES, required=False)
    timeline = forms.ChoiceField(choices=TIMELINE_CHOICES, required=False)

    # Honeypot anti-spam field
    website = forms.CharField(required=False, widget=forms.HiddenInput())
    submission_token = forms.CharField(required=False, widget=forms.HiddenInput())

    _token_signer = signing.TimestampSigner(salt="contact-form")

    class Meta:
        model = ContactInquiry
        fields = [
            "name",
            "email",
            "company",
            "project_type",
            "location",
            "budget_range",
            "timeline",
            "message",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Your name", "aria-describedby": "id_name_error"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Email address", "aria-describedby": "id_email_error"}
            ),
            "company": forms.TextInput(
                attrs={"placeholder": "Company or organisation (optional)"}
            ),
            "location": forms.TextInput(
                attrs={"placeholder": "Project location (optional)"}
            ),
            "message": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Describe your project…",
                    "aria-describedby": "id_message_hint id_message_error",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            issued_at = int(time.time())
            self.initial.setdefault("submission_token", self._token_signer.sign(str(issued_at)))

    def clean_website(self) -> str:
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError(INVALID_SUBMISSION_MESSAGE)
        return ""

    def clean(self):
        cleaned_data = super().clean() or {}
        if self.errors:
            return cleaned_data

        token = cleaned_data.get("submission_token", "")
        if not token:
            raise forms.ValidationError(INVALID_SUBMISSION_MESSAGE)

        max_age = getattr(settings, "CONTACT_FORM_TOKEN_MAX_AGE_SECONDS", 86_400)
        min_age = getattr(settings, "CONTACT_FORM_MIN_AGE_SECONDS", 3)

        try:
            issued_at = int(self._token_signer.unsign(token, max_age=max_age))
        except (signing.BadSignature, ValueError):
            raise forms.ValidationError(INVALID_SUBMISSION_MESSAGE) from None

        age = int(time.time()) - issued_at
        if age < min_age:
            raise forms.ValidationError("Please wait a moment and try again.")

        return cleaned_data

    def focus_first_error(self) -> None:
        for name, field in self.fields.items():
            if name in self.errors and not field.widget.is_hidden:
                field.widget.attrs["autofocus"] = "autofocus"
                break

    def clean_name(self) -> str:
        name = self.cleaned_data.get("name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name

    def clean_message(self) -> str:
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 20:
            raise forms.ValidationError(
                "Please provide a brief description of your enquiry (at least 20 characters)."
            )
        return message
