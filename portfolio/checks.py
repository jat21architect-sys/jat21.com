"""
Custom Django system checks for the portfolio app.

These run automatically via `manage.py check` and `manage.py check --deploy`,
and are registered when the app is ready (see apps.py).
"""

from django.conf import settings
from django.core.checks import Warning, register

# Backends that should never reach production.
_DEV_EMAIL_BACKENDS = {
    "django.core.mail.backends.console.EmailBackend",
    "django.core.mail.backends.dummy.EmailBackend",
    "django.core.mail.backends.locmem.EmailBackend",
}


@register()
def check_production_email_backend(app_configs, **kwargs):
    """
    Warn when a non-SMTP email backend is active in a production-like environment.

    This check fires when DEBUG=False and EMAIL_BACKEND is one of the
    development-only backends (console, dummy, locmem). In that state the
    contact form saves enquiries to the database but sends no email notification,
    so the architect receives no leads — silently.

    Fix: set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    (and the matching EMAIL_HOST / EMAIL_PORT / EMAIL_USE_TLS variables)
    in your production environment.
    """
    errors = []
    if not settings.DEBUG:
        backend = getattr(settings, "EMAIL_BACKEND", "")
        if backend in _DEV_EMAIL_BACKENDS:
            errors.append(
                Warning(
                    f"DEBUG=False (production mode) but EMAIL_BACKEND is '{backend}', "
                    "a dev-only backend that does not deliver email.",
                    hint=(
                        "Set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend "
                        "and configure EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, "
                        "EMAIL_HOST_USER, and EMAIL_HOST_PASSWORD in your environment. "
                        "Without this, contact form enquiries are saved to the database "
                        "but no notification email is sent."
                    ),
                    id="portfolio.W001",
                )
            )
    return errors
