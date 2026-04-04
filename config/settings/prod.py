"""
Production settings.

Activate with:
    DJANGO_SETTINGS_MODULE=config.settings.prod

All values below that are not environment-driven should be safe defaults
for a public deployment. Never set DEBUG=True here.
"""

from .base import *  # noqa: F401, F403
from .base import env  # explicit re-import for clarity

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # must be set in environment
SENTRY_DSN = env.str("SENTRY_DSN", default="")

# ---------------------------------------------------------------------------
# Security hardening
# ---------------------------------------------------------------------------

SECURE_HSTS_SECONDS = 31_536_000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Trust the forwarded-proto header so CSRF and redirects work behind HTTPS proxies.
# List your domain(s) in CSRF_TRUSTED_ORIGINS when deploying.
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])  # pyright: ignore[reportArgumentType]

SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# ---------------------------------------------------------------------------
# Media storage — Cloudinary
# ---------------------------------------------------------------------------
# Overrides the local-filesystem default from base.py.
# Requires CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
# to be set in the environment.
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# ---------------------------------------------------------------------------
# Error visibility — Sentry (optional but strongly recommended)
# ---------------------------------------------------------------------------

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    _sentry_release = env.str("SENTRY_RELEASE", default="")
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=env.str("SENTRY_ENVIRONMENT", default="production"),
        release=_sentry_release or None,
        send_default_pii=env.bool("SENTRY_SEND_DEFAULT_PII", default=False),
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
    )

# ---------------------------------------------------------------------------
# Logging — surface warnings and errors in the hosting platform's log stream
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "apps.site": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.contact": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
