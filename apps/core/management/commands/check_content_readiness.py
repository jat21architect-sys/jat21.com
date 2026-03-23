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
from apps.projects.models import Project, Testimonial
from apps.services.models import Service

_DEMO_SITE_NAME = "Demo Architecture Studio"
_DEMO_CONTACT_EMAIL = "hello@demo-architecture.example"
_DEMO_TAGLINE = "Architectural design shaped by context, clarity, and identity."
_DEMO_META_DESCRIPTION = (
    "An architecture practice whose work combines spatial clarity, "
    "contextual sensitivity, and thoughtful design to create places with identity, "
    "purpose, and lasting value."
)
_DEMO_SITE_LOCATION = "Your City, Your Country"
_DEMO_ABOUT_HEADLINE = "An architect whose work is shaped by context, clarity, and care."
_DEMO_ABOUT_LOCATION = "Your City"
_PLACEHOLDER_MARKERS = (
    "[Your Name]",
    "[Your Local Professional Body]",
    "[Your Professional Institute]",
)
_DEMO_PROJECT_TITLES = {
    "House on the Hillside",
    "Community Library Pavilion",
    "Urban Apartment Retrofit",
    "Commercial Office Conversion",
}
_DEMO_TESTIMONIAL_NAMES = {
    "Sarah & Mark L.",
    "A. Navarro",
    "C. Brennan",
}


def _contains_placeholder_marker(*values: str) -> bool:
    return any(marker in value for marker in _PLACEHOLDER_MARKERS for value in values if value)


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

    if not site.site_name:
        warnings.append(
            "SiteSettings.site_name is blank. "
            "Update it in admin \u2192 Site Settings."
        )
    elif site.site_name == _DEMO_SITE_NAME:
        warnings.append(
            f"SiteSettings.site_name is still the starter value ('{_DEMO_SITE_NAME}'). "
            "Replace it with your real practice name in admin \u2192 Site Settings."
        )

    if not site.contact_email:
        warnings.append(
            "SiteSettings.contact_email is blank. "
            "Set the public contact email in admin \u2192 Site Settings."
        )
    elif site.contact_email == _DEMO_CONTACT_EMAIL:
        warnings.append(
            f"SiteSettings.contact_email is still the starter value ('{_DEMO_CONTACT_EMAIL}'). "
            "Replace the public contact email in admin \u2192 Site Settings."
        )

    if site.tagline == _DEMO_TAGLINE:
        warnings.append(
            "SiteSettings.tagline is still the starter copy. "
            "Replace it with your own one-line positioning statement."
        )

    if not site.meta_description:
        warnings.append(
            "SiteSettings.meta_description is blank. "
            "The homepage will have no meta description in search results."
        )
    elif site.meta_description == _DEMO_META_DESCRIPTION:
        warnings.append(
            "SiteSettings.meta_description is still the starter copy. "
            "Replace it with a real homepage SEO description."
        )

    if not site.og_image:
        warnings.append(
            "SiteSettings.og_image is missing. "
            "Social share cards will have no image."
        )

    if site.location == _DEMO_SITE_LOCATION:
        warnings.append(
            "SiteSettings.location is still the starter placeholder ('Your City, Your Country'). "
            "Replace it with your real public location or leave it blank."
        )

    # -- AboutProfile ---------------------------------------------------------

    if not about.headline:
        warnings.append(
            "AboutProfile.headline is blank. "
            "The About page will render without a heading."
        )
    elif about.headline == _DEMO_ABOUT_HEADLINE:
        warnings.append(
            "AboutProfile.headline is still the starter copy. "
            "Replace it with your real About-page heading."
        )

    if about.experience_years == 0:
        warnings.append(
            "AboutProfile.experience_years is 0. "
            "This value renders publicly \u2014 enter the real figure in admin."
        )

    if not about.portrait:
        warnings.append(
            "AboutProfile.portrait is missing. "
            "The About page will have no portrait image."
        )

    if _contains_placeholder_marker(about.intro, about.biography, about.credentials):
        warnings.append(
            "AboutProfile still contains starter placeholder markers such as '[Your Name]'. "
            "Replace the About copy before launch."
        )

    if about.location == _DEMO_ABOUT_LOCATION:
        warnings.append(
            "AboutProfile.location is still the starter placeholder ('Your City'). "
            "Replace it with your real location or leave it blank."
        )

    # -- Content collections --------------------------------------------------

    if not Service.objects.filter(active=True).exists():
        warnings.append(
            "No active Service records found. "
            "The Services page will be empty."
        )

    projects = Project.objects.all()
    if not projects.exists():
        warnings.append(
            "No Project records found. "
            "The portfolio will be empty."
        )
    else:
        demo_project_titles = sorted(
            title for title in projects.values_list("title", flat=True) if title in _DEMO_PROJECT_TITLES
        )
        if demo_project_titles:
            warnings.append(
                "Starter Project records are still present: "
                + ", ".join(demo_project_titles)
                + ". Replace or delete them before launch."
            )

    demo_testimonial_names = sorted(
        name
        for name in Testimonial.objects.values_list("name", flat=True)
        if name in _DEMO_TESTIMONIAL_NAMES
    )
    if demo_testimonial_names:
        warnings.append(
            "Starter Testimonial records are still present: "
            + ", ".join(demo_testimonial_names)
            + ". Replace or delete them before launch."
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
