import logging

from django.conf import settings as django_settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LEGACY_PROJECT_TYPE_MAP, PROJECT_TYPE_CHOICES, ContactForm

logger = logging.getLogger(__name__)

DELIVERY_STATUS_SENT = "sent"
DELIVERY_STATUS_SAVED_ONLY_MISSING_CONTACT_EMAIL = "saved_only_missing_contact_email"
DELIVERY_STATUS_SAVED_ONLY_DELIVERY_FAILED = "saved_only_delivery_failed"

PUBLIC_DELIVERY_OUTCOME_SENT = "sent"
PUBLIC_DELIVERY_OUTCOME_SAVED_ONLY = "saved-only"
VALID_PUBLIC_DELIVERY_OUTCOMES = {
    PUBLIC_DELIVERY_OUTCOME_SENT,
    PUBLIC_DELIVERY_OUTCOME_SAVED_ONLY,
}


# ---------------------------------------------------------------------------
# Contact form
# ---------------------------------------------------------------------------


def _client_ip(request) -> str:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _public_delivery_outcome(delivery_status: str) -> str:
    if delivery_status == DELIVERY_STATUS_SENT:
        return PUBLIC_DELIVERY_OUTCOME_SENT
    return PUBLIC_DELIVERY_OUTCOME_SAVED_ONLY


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            client_ip = _client_ip(request) or "unknown"
            # Notify the configured inbox — failure is non-fatal (form already saved to DB).
            # Reply-To is set so the recipient can reply directly from their email client.
            notification_recipient = getattr(django_settings, "CONTACT_EMAIL", "").strip()
            if not notification_recipient:
                email_delivery = DELIVERY_STATUS_SAVED_ONLY_MISSING_CONTACT_EMAIL
                logger.warning(
                    "Contact email delivery skipped for inquiry pk=%s because CONTACT_EMAIL is blank",
                    inquiry.pk,
                )
            else:
                try:
                    msg = EmailMessage(
                        subject=f"New enquiry from {inquiry.name}",
                        body=(
                            f"Name: {inquiry.name}\n"
                            f"Email: {inquiry.email}\n"
                            f"Company: {inquiry.company}\n"
                            f"Project type: {inquiry.project_type}\n"
                            f"Location: {inquiry.location}\n"
                            f"Budget: {inquiry.budget_range}\n"
                            f"Timeline: {inquiry.timeline}\n\n"
                            f"Message:\n{inquiry.message}"
                        ),
                        from_email=django_settings.DEFAULT_FROM_EMAIL,
                        to=[notification_recipient],
                        reply_to=[inquiry.email],
                    )
                    msg.send()
                    email_delivery = DELIVERY_STATUS_SENT
                except Exception:
                    email_delivery = DELIVERY_STATUS_SAVED_ONLY_DELIVERY_FAILED
                    logger.exception("Contact email failed for inquiry pk=%s", inquiry.pk)
            logger.info(
                "Contact inquiry saved pk=%s email=%s ip=%s email_delivery=%s",
                inquiry.pk,
                inquiry.email,
                client_ip,
                email_delivery,
            )
            public_delivery_outcome = _public_delivery_outcome(email_delivery)
            return redirect(
                f"{reverse('contact:success')}?delivery={public_delivery_outcome}"
            )
        form.focus_first_error()
        client_ip = _client_ip(request) or "unknown"
        if request.POST.get("website"):
            logger.warning("Contact form honeypot triggered ip=%s", client_ip)
        elif form.non_field_errors():
            logger.warning(
                "Contact form anti-bot token rejected ip=%s errors=%s",
                client_ip,
                "; ".join(str(error) for error in form.non_field_errors()),
            )
    else:
        initial: dict[str, str] = {}
        project_type = request.GET.get("project_type", "").strip()
        if project_type:
            valid_types = {c[0] for c in PROJECT_TYPE_CHOICES if c[0]}
            if project_type in valid_types:
                initial["project_type"] = project_type
            elif project_type in LEGACY_PROJECT_TYPE_MAP:
                initial["project_type"] = LEGACY_PROJECT_TYPE_MAP[project_type]
        form = ContactForm(initial=initial)
    return render(request, "contact/contact.html", {"form": form})


def contact_success_view(request):
    delivery_outcome = request.GET.get("delivery", PUBLIC_DELIVERY_OUTCOME_SENT)
    if delivery_outcome not in VALID_PUBLIC_DELIVERY_OUTCOMES:
        delivery_outcome = PUBLIC_DELIVERY_OUTCOME_SENT
    return render(
        request,
        "contact/contact_success.html",
        {"delivery_outcome": delivery_outcome},
    )
