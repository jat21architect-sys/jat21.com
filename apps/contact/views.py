import logging

from django.conf import settings as django_settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .forms import LEGACY_PROJECT_TYPE_MAP, PROJECT_TYPE_CHOICES, ContactForm

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Contact form
# ---------------------------------------------------------------------------


def _client_ip(request) -> str:
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            client_ip = _client_ip(request) or "unknown"
            # Notify the configured inbox — failure is non-fatal (form already saved to DB).
            # Reply-To is set so the recipient can reply directly from their email client.
            email_delivery = "sent"
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
                    to=[django_settings.CONTACT_EMAIL],
                    reply_to=[inquiry.email],
                )
                msg.send()
            except Exception:
                email_delivery = "failed"
                logger.exception("Contact email failed for inquiry pk=%s", inquiry.pk)
            logger.info(
                "Contact inquiry saved pk=%s email=%s ip=%s email_delivery=%s",
                inquiry.pk,
                inquiry.email,
                client_ip,
                email_delivery,
            )
            return redirect("contact:success")
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
    return render(request, "contact/contact_success.html")
