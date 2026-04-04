"""
Base Django settings shared by all environments.

Do not use this module directly. Import dev or prod instead.
"""

from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# config/settings/base.py → config/settings/ → config/ → project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()

# Read .env from project root if it exists (not required in CI/prod)
_dotenv = BASE_DIR / ".env"
if _dotenv.exists():
    environ.Env.read_env(_dotenv)

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

# Safe default — overridden to True in dev.py only.
# If base settings are ever used directly, the server does not expose debug info.
DEBUG = False

SECRET_KEY = env("SECRET_KEY")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "cloudinary_storage",
    "cloudinary",
    "apps.core.apps.CoreConfig",
    "apps.site.apps.SiteConfigApp",
    "apps.pages.apps.PagesConfig",
    "apps.projects.apps.ProjectsConfig",
    "apps.contact.apps.ContactConfig",
    "apps.services.apps.ServicesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database — SQLite by default; set DATABASE_URL in environment for Postgres
# ---------------------------------------------------------------------------

_db_url = env.str("DATABASE_URL", default="")
if _db_url:
    DATABASES = {"default": env.db("DATABASE_URL")}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static and media files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Cloudinary — persistent media storage for production
# ---------------------------------------------------------------------------
# Credentials are read from the environment; left empty here so dev continues
# to use the local filesystem. Set DEFAULT_FILE_STORAGE in prod.py to activate.
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env.str("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": env.str("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": env.str("CLOUDINARY_API_SECRET", default=""),
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Email (environment-driven; environments override as needed)
# ---------------------------------------------------------------------------

EMAIL_BACKEND = env.str(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env.str("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
# The address that receives contact-form notification emails.
# MUST be set in the production environment — no personal default is provided.
CONTACT_EMAIL = env.str("CONTACT_EMAIL", default="")
# The "From" address on outgoing mail. Falls back to CONTACT_EMAIL so a single
# env var covers most deployments. Set DEFAULT_FROM_EMAIL explicitly to use a
# separate noreply@ sender.
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default=CONTACT_EMAIL)
