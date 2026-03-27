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

from apps.core.about_defaults import (
    PRACTICE_STRUCTURE_PROMPT,
    PROFESSIONAL_STANDING_PROMPT,
    PROJECT_LEADERSHIP_PROMPT,
)
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
_DEMO_ABOUT_ONE_LINE = "Architecture shaped by context, use, and urban climate."
_DEMO_ABOUT_PRACTICE_SUMMARY = (
    "Demo Architecture Studio is a practice working across housing, civic buildings, "
    "and workplace projects in northern urban settings."
)
_DEMO_ABOUT_PROJECT_LEADERSHIP = (
    "Projects are led by a compact studio team, with specialist consultants involved as "
    "needed for structure, building services, and planning coordination."
)
_PLACEHOLDER_MARKERS = (
    "[Your Name]",
    "[Your Local Professional Body]",
    "[Your Professional Institute]",
    "[Add ",
    "[Describe ",
    "[Explain ",
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


def _concrete_lines(value: str) -> list[str]:
    return [
        line.strip()
        for line in value.splitlines()
        if line.strip() and not _contains_placeholder_marker(line)
    ]


def collect_readiness_issues() -> tuple[list[str], list[str]]:
    """
    Return (blockers, warnings) describing content that still looks like an
    uncustomised template or lacks the minimum facts needed for launch.

    Separated from the Command class so it can be called directly in tests.
    """
    blockers: list[str] = []
    warnings: list[str] = []

    site = SiteSettings.load()
    about = AboutProfile.load()

    # -- SiteSettings ---------------------------------------------------------

    if not site.site_name:
        blockers.append(
            "SiteSettings.site_name is blank. "
            "Update it in admin \u2192 Site Settings."
        )
    elif site.site_name == _DEMO_SITE_NAME:
        blockers.append(
            f"SiteSettings.site_name is still the starter value ('{_DEMO_SITE_NAME}'). "
            "Replace it with your real practice name in admin \u2192 Site Settings."
        )

    if not site.contact_email:
        blockers.append(
            "SiteSettings.contact_email is blank. "
            "Set the public contact email in admin \u2192 Site Settings."
        )
    elif site.contact_email == _DEMO_CONTACT_EMAIL:
        blockers.append(
            f"SiteSettings.contact_email is still the starter value ('{_DEMO_CONTACT_EMAIL}'). "
            "Replace the public contact email in admin \u2192 Site Settings."
        )

    if site.tagline == _DEMO_TAGLINE:
        blockers.append(
            "SiteSettings.tagline is still the starter copy. "
            "Replace it with your own one-line positioning statement."
        )

    if not site.meta_description:
        blockers.append(
            "SiteSettings.meta_description is blank. "
            "The homepage will have no meta description in search results."
        )
    elif site.meta_description == _DEMO_META_DESCRIPTION:
        blockers.append(
            "SiteSettings.meta_description is still the starter copy. "
            "Replace it with a real homepage SEO description."
        )

    if not site.og_image:
        warnings.append(
            "SiteSettings.og_image is missing. "
            "The site will fall back to the bundled default share image; upload a custom image for branded previews."
        )

    if not site.about_meta_description:
        warnings.append(
            "SiteSettings.about_meta_description is blank. "
            "The About page will fall back to the homepage meta description."
        )

    if not site.services_meta_description:
        warnings.append(
            "SiteSettings.services_meta_description is blank. "
            "The Services page will fall back to the homepage meta description."
        )

    if not site.projects_meta_description:
        warnings.append(
            "SiteSettings.projects_meta_description is blank. "
            "The Projects page will fall back to the homepage meta description."
        )

    if not site.contact_meta_description:
        warnings.append(
            "SiteSettings.contact_meta_description is blank. "
            "The Contact page will fall back to the homepage meta description."
        )

    if not site.location:
        blockers.append(
            "SiteSettings.location is blank. "
            "Set a real public location in admin \u2192 Site Settings."
        )
    elif site.location == _DEMO_SITE_LOCATION:
        blockers.append(
            "SiteSettings.location is still the starter placeholder ('Your City, Your Country'). "
            "Replace it with your real public location."
        )

    # -- AboutProfile ---------------------------------------------------------

    if (
        about.identity_mode == AboutProfile.IdentityMode.PERSON
        and not about.principal_name
    ):
        blockers.append(
            "AboutProfile.principal_name is blank for a person-led About page. "
            "Set the public name of the principal before launch."
        )

    if (
        about.identity_mode == AboutProfile.IdentityMode.PERSON
        and not about.principal_title
    ):
        blockers.append(
            "AboutProfile.principal_title is blank for a person-led About page. "
            "Set the public role/title before launch."
        )

    if not about.practice_structure:
        blockers.append(
            "AboutProfile.practice_structure is blank. "
            "Add a truthful practice structure such as 'Solo practice' or 'Small studio'."
        )
    elif about.practice_structure == PRACTICE_STRUCTURE_PROMPT:
        blockers.append(
            "AboutProfile.practice_structure is still a starter prompt. "
            "Replace it with the truthful public practice structure."
        )

    if not about.one_line_practice_description:
        blockers.append(
            "AboutProfile.one_line_practice_description is blank. "
            "Add the public one-line practice description for the About hero."
        )
    elif about.one_line_practice_description == _DEMO_ABOUT_ONE_LINE:
        blockers.append(
            "AboutProfile.one_line_practice_description is still demo/reference copy. "
            "Replace it with your real public practice description."
        )

    if not about.practice_summary:
        blockers.append(
            "AboutProfile.practice_summary is blank. "
            "Add a factual summary of what the practice does and the kind of work it takes on."
        )
    elif _DEMO_ABOUT_PRACTICE_SUMMARY in about.practice_summary:
        blockers.append(
            "AboutProfile.practice_summary is still demo/reference copy. "
            "Replace it with your own About summary before launch."
        )

    if not about.project_leadership:
        blockers.append(
            "AboutProfile.project_leadership is blank. "
            "Explain how projects are led and where consultants or collaborators fit in."
        )
    elif about.project_leadership == PROJECT_LEADERSHIP_PROMPT:
        blockers.append(
            "AboutProfile.project_leadership is still a starter prompt. "
            "Replace it with the real project leadership statement shown on the About page."
        )
    elif about.project_leadership == _DEMO_ABOUT_PROJECT_LEADERSHIP:
        blockers.append(
            "AboutProfile.project_leadership is still demo/reference copy. "
            "Replace it with your real project leadership statement."
        )

    if not about.professional_standing:
        blockers.append(
            "AboutProfile.professional_standing is blank. "
            "Add the public registration or professional standing shown on the About page."
        )
    elif about.professional_standing == PROFESSIONAL_STANDING_PROMPT:
        blockers.append(
            "AboutProfile.professional_standing is still a starter prompt. "
            "Replace it with the real public registration or professional standing."
        )

    if about.experience_years == 0:
        blockers.append(
            "AboutProfile.experience_years is 0. "
            "This value renders publicly \u2014 enter the real figure in admin."
        )

    if not about.approach:
        blockers.append(
            "AboutProfile.approach is blank. "
            "Add a short practical approach statement for the About page."
        )

    if not about.closing_invitation:
        blockers.append(
            "AboutProfile.closing_invitation is blank. "
            "Add the short closing invitation shown above the contact CTA."
        )

    if not (_concrete_lines(about.education) or _concrete_lines(about.supporting_facts)):
        blockers.append(
            "AboutProfile needs at least one concrete supporting fact. "
            "Add education and/or supporting facts so the public professional profile is grounded in real evidence."
        )

    if (
        about.portrait_mode == AboutProfile.PortraitMode.PORTRAIT
        and not about.portrait
    ):
        blockers.append(
            "AboutProfile.portrait_mode is set to show a portrait, but no portrait file is uploaded."
        )
    elif about.portrait_mode == AboutProfile.PortraitMode.TEXT_ONLY:
        warnings.append(
            "AboutProfile is using text-only mode. This is allowed, but the About page will be stronger with a real portrait."
        )

    if _contains_placeholder_marker(
        about.principal_name,
        about.principal_title,
        about.one_line_practice_description,
        about.practice_summary,
        about.approach,
        about.closing_invitation,
    ):
        blockers.append(
            "AboutProfile still contains starter placeholder markers such as '[Add ...]'. "
            "Replace the About copy before launch."
        )

    # -- Content collections --------------------------------------------------

    if not Service.objects.filter(active=True).exists():
        blockers.append(
            "No active Service records found. "
            "The Services page will be empty."
        )

    projects = Project.objects.all()
    if not projects.exists():
        blockers.append(
            "No Project records found. "
            "The portfolio will be empty."
        )
    else:
        demo_project_titles = sorted(
            title for title in projects.values_list("title", flat=True) if title in _DEMO_PROJECT_TITLES
        )
        if demo_project_titles:
            blockers.append(
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
        blockers.append(
            "Starter Testimonial records are still present: "
            + ", ".join(demo_testimonial_names)
            + ". Replace or delete them before launch."
        )

    return blockers, warnings


def collect_warnings() -> list[str]:
    blockers, warnings = collect_readiness_issues()
    return blockers + warnings


class Command(BaseCommand):
    help = (
        "Check that the site has been properly customised from template defaults "
        "before launch. Exits with code 1 if any warnings are reported."
    )

    def handle(self, *args, **options):
        blockers, warnings = collect_readiness_issues()

        if blockers or warnings:
            self.stdout.write(
                self.style.WARNING(
                    f"\n{len(blockers)} blocking issue(s), {len(warnings)} warning(s) found:\n"
                )
            )
            for blocker in blockers:
                self.stdout.write(self.style.ERROR(f"  \u2716  {blocker}"))
            for warning in warnings:
                self.stdout.write(self.style.WARNING(f"  \u26a0  {warning}"))
            self.stdout.write("")
            if blockers:
                sys.exit(1)
            return

        self.stdout.write(self.style.SUCCESS("Content readiness: all checks pass.\n"))
