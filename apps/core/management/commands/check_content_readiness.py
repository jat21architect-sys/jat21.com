"""
Management command: check_content_readiness
-------------------------------------------
Checks that the site has been customised from template defaults and has the
minimum content needed for a public launch.

Exit code 0 — all checks pass.
Exit code 1 — at least one warning was reported.

Usage:
    uv run python manage.py check_content_readiness
    # or via Make:
    make check-content

Suitable as a pre-launch gate.  Add to a deploy checklist, not to `make health`
(health is CI-safe; this command requires a populated database).
"""

import sys

from django.core.management.base import BaseCommand

from apps.core.models import AboutProfile, SiteSettings
from apps.projects.models import Project
from apps.services.models import Service

# ---------------------------------------------------------------------------
# Template defaults — strings baked into model field default= values.
# If the DB still contains them, the site has not been properly customised.
# ---------------------------------------------------------------------------

_DEFAULT_SITE_NAME = "Jeannot Tsirenge"
_DEFAULT_TAGLINE = "Architectural design shaped by context, clarity, and identity."
_DEFAULT_CONTACT_EMAIL = "contact@jeannot-tsirenge.com"  # matches SiteSettings model default


def collect_warnings() -> list[str]:
    """
    Return a list of human-readable warning strings describing content that
    still looks like an uncustomised template.  Returns an empty list when
    the site passes all checks.

    Separated from the Command class so it can be called directly in tests.
    """
    warnings: list[str] = []

    site = SiteSettings.load()
    about = AboutProfile.load()

    # -- SiteSettings ---------------------------------------------------------

    if site.site_name == _DEFAULT_SITE_NAME:
        warnings.append(
            f"SiteSettings.site_name is still the template default ('{_DEFAULT_SITE_NAME}'). "
            "Update it in admin → Site Settings."
        )

    if site.tagline == _DEFAULT_TAGLINE:
        warnings.append(
            "SiteSettings.tagline is still the template default. "
            "Update it in admin → Site Settings."
        )

    if site.contact_email == _DEFAULT_CONTACT_EMAIL:
        warnings.append(
            f"SiteSettings.contact_email is still the template default ('{_DEFAULT_CONTACT_EMAIL}'). "
            "Enquiries will go to the wrong inbox."
        )

    if not site.meta_description:
        warnings.append(
            "SiteSettings.meta_description is blank. "
            "The homepage will have no meta description in search results."
        )

    if not site.og_image:
        warnings.append(
            "SiteSettings.og_image is missing. "
            "Social share cards will have no image."
        )

    # -- AboutProfile ---------------------------------------------------------

    if not about.headline:
        warnings.append(
            "AboutProfile.headline is blank. "
            "The About page will render without a heading."
        )

    if about.experience_years == 0:
        warnings.append(
            "AboutProfile.experience_years is 0. "
            "This value renders publicly — enter the real figure in admin."
        )

    if not about.portrait:
        warnings.append(
            "AboutProfile.portrait is missing. "
            "The About page will have no portrait image."
        )

    # -- Content collections --------------------------------------------------

    if not Service.objects.filter(active=True).exists():
        warnings.append(
            "No active Service records found. "
            "The Services page will be empty."
        )

    if not Project.objects.exists():
        warnings.append(
            "No Project records found. "
            "The portfolio will be empty."
        )

    return warnings


class Command(BaseCommand):
    help = (
        "Check that the site has been properly customised from template defaults "
        "before launch. Exits with code 1 if any warnings are reported."
    )

    def handle(self, *args, **options):
        warnings = collect_warnings()

        if warnings:
            self.stdout.write(
                self.style.WARNING(f"\n{len(warnings)} content readiness warning(s) found:\n")
            )
            for w in warnings:
                self.stdout.write(self.style.WARNING(f"  \u26a0  {w}"))
            self.stdout.write("")
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("Content readiness: all checks pass.\n"))
