"""
Custom Django system checks for the shared core app.

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
_SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
_CLOUDINARY_STORAGE_BACKEND = "cloudinary_storage.storage.MediaCloudinaryStorage"


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
    errors: list[Warning] = []
    if settings.DEBUG:
        return errors

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
                id="core.W001",
            )
        )
        return errors

    email_host = getattr(settings, "EMAIL_HOST", "")
    if backend == _SMTP_BACKEND and email_host in {"", "localhost"}:
        errors.append(
            Warning(
                "DEBUG=False (production mode) with SMTP email enabled, but EMAIL_HOST "
                f"is still '{email_host or '(empty)'}'.",
                hint=(
                    "Set EMAIL_HOST to your real SMTP server hostname. Leaving it empty "
                    "or at Django's default localhost usually means contact notifications "
                    "will fail in production."
                ),
                id="core.W004",
            )
        )
    return errors


@register()
def check_production_csrf_trusted_origins(app_configs, **kwargs):
    """Warn when production CSRF trusted origins are missing or not HTTPS."""
    errors: list[Warning] = []
    if settings.DEBUG:
        return errors

    origins = list(getattr(settings, "CSRF_TRUSTED_ORIGINS", []))
    if not origins:
        errors.append(
            Warning(
                "DEBUG=False (production mode) but CSRF_TRUSTED_ORIGINS is empty.",
                hint=(
                    "Set CSRF_TRUSTED_ORIGINS to your HTTPS site origin(s), e.g. "
                    "https://yourdomain.com,https://www.yourdomain.com. "
                    "Without this, admin and contact form POSTs can fail behind a reverse proxy."
                ),
                id="core.W002",
            )
        )
        return errors

    invalid_origins = [origin for origin in origins if not origin.startswith("https://")]
    if invalid_origins:
        errors.append(
            Warning(
                "CSRF_TRUSTED_ORIGINS contains non-HTTPS origin(s): "
                + ", ".join(invalid_origins),
                hint=(
                    "Production CSRF trusted origins should use HTTPS origins only, e.g. "
                    "https://yourdomain.com."
                ),
                id="core.W002",
            )
        )
    return errors


@register()
def check_production_media_storage_credentials(app_configs, **kwargs):
    """Warn when production media storage is enabled without Cloudinary credentials."""
    errors: list[Warning] = []
    if settings.DEBUG:
        return errors

    storage_backend = getattr(settings, "DEFAULT_FILE_STORAGE", "")
    if storage_backend != _CLOUDINARY_STORAGE_BACKEND:
        return errors

    cloudinary_settings = getattr(settings, "CLOUDINARY_STORAGE", {})
    missing = [
        env_name
        for env_name, key in (
            ("CLOUDINARY_CLOUD_NAME", "CLOUD_NAME"),
            ("CLOUDINARY_API_KEY", "API_KEY"),
            ("CLOUDINARY_API_SECRET", "API_SECRET"),
        )
        if not cloudinary_settings.get(key)
    ]
    if missing:
        errors.append(
            Warning(
                "Production media storage is set to Cloudinary, but Cloudinary credentials are missing: "
                + ", ".join(missing),
                hint=(
                    "Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and "
                    "CLOUDINARY_API_SECRET in the production environment. Without them, "
                    "admin-managed uploads will fail at runtime."
                ),
                id="core.W003",
            )
        )
    return errors


@register()
def check_production_sentry_dsn(app_configs, **kwargs):
    """Warn when production error reporting has not been configured."""
    errors: list[Warning] = []
    if settings.DEBUG:
        return errors

    if not getattr(settings, "SENTRY_DSN", ""):
        errors.append(
            Warning(
                "DEBUG=False (production mode) but SENTRY_DSN is empty.",
                hint=(
                    "Set SENTRY_DSN to your Sentry project's DSN so uncaught production "
                    "exceptions are captured outside the hosting platform logs."
                ),
                id="core.W005",
            )
        )
    return errors


@register()
def check_contact_email_default(app_configs, **kwargs):
    """
    Warn when CONTACT_EMAIL is not configured in production.

    Without this setting, contact form submissions are saved to the database
    but no notification email reaches the site owner.
    """
    errors: list[Warning] = []
    if settings.DEBUG:
        return errors

    contact_email = getattr(settings, "CONTACT_EMAIL", "")
    if not contact_email:
        errors.append(
            Warning(
                "CONTACT_EMAIL is not set.",
                hint=(
                    "Set CONTACT_EMAIL to your monitored inbox in the production environment. "
                    "Without this, contact form notifications are never delivered."
                ),
                id="core.W006",
            )
        )
    return errors
