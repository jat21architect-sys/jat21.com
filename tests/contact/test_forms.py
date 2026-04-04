"""
Contact form tests — valid POST creates a ContactInquiry; invalid POST stays on page.
"""

import time

import pytest
from django.core.signing import TimestampSigner
from django.test import override_settings
from django.urls import reverse

from apps.contact.models import ContactInquiry


def valid_submission_token(age_seconds: int = 10) -> str:
    issued_at = int(time.time()) - age_seconds
    return TimestampSigner(salt="contact-form").sign(str(issued_at))


def make_payload(**overrides):
    payload = {
        "name": "Alice Architect",
        "email": "alice@example.com",
        "message": "I would like to discuss a residential project.",
        "project_type": "Housing",
        "budget_range": "500k – 1M",
        "timeline": "3–6 months",
        "submission_token": valid_submission_token(),
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
@override_settings(CONTACT_EMAIL="notify@example.com", DEFAULT_FROM_EMAIL="no-reply@example.com")
def test_contact_form_valid_post_creates_inquiry(client, site_settings):
    assert ContactInquiry.objects.count() == 0
    response = client.post(reverse("contact:contact"), data=make_payload(), follow=False)
    # Should redirect to the thank-you page
    assert response.status_code == 302
    assert response["Location"] == f"{reverse('contact:success')}?delivery=sent"
    assert ContactInquiry.objects.count() == 1

    inquiry = ContactInquiry.objects.get(email="alice@example.com")
    assert inquiry.name == "Alice Architect"
    assert inquiry.email == "alice@example.com"
    assert inquiry.status == "new"


@pytest.mark.django_db
def test_contact_form_missing_required_fields_stays_on_page(client, site_settings):
    response = client.post(reverse("contact:contact"), data={"name": "", "email": "", "message": ""})
    assert response.status_code == 200
    assert b"Please wait a moment and try again." not in response.content
    assert response.context["form"].fields["name"].widget.attrs.get("autofocus") == "autofocus"
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
def test_contact_form_invalid_email(client, site_settings):
    payload = make_payload(email="not-an-email")
    response = client.post(reverse("contact:contact"), data=payload)
    assert response.status_code == 200
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
def test_contact_form_focuses_first_invalid_field(client, site_settings):
    payload = make_payload(email="not-an-email")
    response = client.post(reverse("contact:contact"), data=payload)
    assert response.status_code == 200

    form = response.context["form"]
    assert form.fields["name"].widget.attrs.get("autofocus") is None
    assert form.fields["email"].widget.attrs.get("autofocus") == "autofocus"


@pytest.mark.django_db
def test_honeypot_filled_rejects_submission(client, site_settings):
    """A submission with the honeypot field filled should be silently rejected."""
    payload = make_payload(website="http://spam.example.com")
    response = client.post(reverse("contact:contact"), data=payload)
    assert response.status_code == 200
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
def test_short_message_rejected(client, site_settings):
    """Messages shorter than 20 characters should fail validation."""
    payload = make_payload(message="Too short.")
    response = client.post(reverse("contact:contact"), data=payload)
    assert response.status_code == 200
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
def test_contact_form_submitted_too_quickly_rejected(client, site_settings):
    payload = make_payload(submission_token=valid_submission_token(age_seconds=0))
    response = client.post(reverse("contact:contact"), data=payload)
    assert response.status_code == 200
    assert b"Please wait a moment and try again." in response.content
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
def test_contact_form_invalid_token_uses_actionable_reload_message(client, site_settings):
    payload = make_payload(submission_token="not-a-valid-token")
    response = client.post(reverse("contact:contact"), data=payload)

    assert response.status_code == 200
    assert b"This form expired or became invalid. Reload the page and try again." in response.content
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
@override_settings(CONTACT_EMAIL="", DEFAULT_FROM_EMAIL="")
def test_contact_form_saves_inquiry_without_send_when_contact_email_missing(
    client, site_settings, monkeypatch, caplog
):
    """
    If CONTACT_EMAIL is blank the inquiry is still saved, no send attempt runs,
    and the public flow switches to the saved-only success state.
    """
    from django.core.mail import EmailMessage as DjangoEmailMessage

    called = False

    def _send(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("Email send should not run when CONTACT_EMAIL is blank")

    monkeypatch.setattr(DjangoEmailMessage, "send", _send)

    response = client.post(reverse("contact:contact"), data=make_payload(), follow=False)
    assert response.status_code == 302
    assert response["Location"] == f"{reverse('contact:success')}?delivery=saved-only"
    assert ContactInquiry.objects.count() == 1
    assert called is False
    assert "CONTACT_EMAIL is blank" in caplog.text


@pytest.mark.django_db
@override_settings(CONTACT_EMAIL="notify@example.com", DEFAULT_FROM_EMAIL="no-reply@example.com")
def test_contact_form_saves_inquiry_even_when_email_send_fails(client, site_settings, monkeypatch, caplog):
    """
    If the email backend raises an exception the inquiry must still be saved
    and the user must still be redirected to the saved-only success state.
    The send failure is logged but must never surface as an HTTP 500.
    """
    from django.core.mail import EmailMessage as DjangoEmailMessage

    def _raise(*args, **kwargs):
        raise OSError("SMTP server unavailable")

    monkeypatch.setattr(DjangoEmailMessage, "send", _raise)

    response = client.post(reverse("contact:contact"), data=make_payload(), follow=False)
    assert response.status_code == 302
    assert response["Location"] == f"{reverse('contact:success')}?delivery=saved-only"
    assert ContactInquiry.objects.count() == 1
    assert "Contact email failed for inquiry" in caplog.text


@pytest.mark.django_db
def test_contact_form_short_name_rejected(client, site_settings):
    """A single-character name is too short and should fail clean_name validation."""
    payload = make_payload(name="A")
    response = client.post(reverse("contact:contact"), data=payload)
    assert response.status_code == 200
    assert ContactInquiry.objects.count() == 0
