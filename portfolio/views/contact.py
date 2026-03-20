import logging

from django.conf import settings as django_settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from ..forms import PROJECT_TYPE_CHOICES, ContactForm

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Contact form
# ---------------------------------------------------------------------------


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            # Notify site owner — failure is non-fatal (form already saved to DB).
            # Reply-To is set so the architect can reply directly from their email client.
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
                logger.exception("Contact email failed for inquiry pk=%s", inquiry.pk)
            return redirect("contact_success")
    else:
        initial: dict[str, str] = {}
        project_type = request.GET.get("project_type", "").strip()
        if project_type:
            valid_types = {c[0] for c in PROJECT_TYPE_CHOICES if c[0]}
            if project_type in valid_types:
                initial["project_type"] = project_type
        form = ContactForm(initial=initial)
    return render(request, "contact.html", {"form": form})


def contact_success_view(request):
    return render(request, "contact_success.html")
