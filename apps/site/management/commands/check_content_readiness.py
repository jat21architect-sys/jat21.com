"""
Management command: check_content_readiness
-------------------------------------------
Checks that the site has been customised from template defaults and has the
minimum content needed for a public launch.

Exit code 0 — all checks pass.
Exit code 1 — at least one blocking launch issue was reported.

Usage:
    uv run python manage.py check_content_readiness
    # or via Make:
    make check-content

Suitable as a pre-launch gate.  Add to a deploy checklist, not to `make health`
(health is CI-safe; this command requires a populated database).
"""

import sys

from django.conf import settings as django_settings
from django.core.management.base import BaseCommand

from apps.core.templatetags.core_tags import (
    NAV_TEXT_MAX_CHARS,
    NAV_TEXT_MAX_WORDS,
    _compute_monogram,
)
from apps.projects.models import Project, Testimonial
from apps.services.models import Service
from apps.site.about_defaults import (
    is_placeholder_text,
    public_lines,
    public_text,
)
from apps.site.models import AboutProfile, SiteSettings

_DEMO_SITE_NAME = "Demo Architecture Studio"
_DEMO_CONTACT_EMAIL = "hello@demo-architecture.example"
_DEMO_TAGLINE = "Architectural design shaped by context, clarity, and identity."
_DEMO_META_DESCRIPTION = (
    "An architecture practice whose work combines spatial clarity, "
    "contextual sensitivity, and thoughtful design to create places with identity, "
    "purpose, and lasting value."
)
_DEMO_SITE_LOCATION = "Your City, Your Country"
_META_BRAND_NAMES = {
    "Demo Architecture Studio",
    "Rossi Meyer Studio",
}
_DEMO_ABOUT_ONE_LINE = "Architecture shaped by context, use, and urban climate."
_DEMO_ABOUT_PRACTICE_SUMMARY = (
    "Demo Architecture Studio is a practice working across housing, civic buildings, "
    "and workplace projects in northern urban settings."
)
_DEMO_ABOUT_PROJECT_LEADERSHIP = (
    "Projects are led by a compact studio team, with specialist consultants involved as "
    "needed for structure, building services, and planning coordination."
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
    return any(is_placeholder_text(value) for value in values if value)


def _concrete_lines(value: str) -> list[str]:
    return public_lines(value)


def _stale_meta_brand(value: str, current_site_name: str) -> str:
    for brand in _META_BRAND_NAMES:
        if brand in value and brand != current_site_name:
            return brand
    return ""


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
    else:
        nav_name_set = bool(site.nav_name.strip())
        logo_set = bool(site.logo)
        normalized_site_name = " ".join(site.site_name.split())
        monogram_triggered = (
            len(normalized_site_name) > NAV_TEXT_MAX_CHARS
            or len(normalized_site_name.split()) > NAV_TEXT_MAX_WORDS
        )
        if len(normalized_site_name) > 30 and not nav_name_set and not logo_set:
            warnings.append(
                "SiteSettings.site_name is longer than 30 characters and no nav_name or logo is set. "
                "The automatic navbar fallback may feel crowded or weak on narrow screens."
            )
        if monogram_triggered and not nav_name_set and not logo_set:
            monogram = _compute_monogram(normalized_site_name)
            if len(monogram) == 1:
                warnings.append(
                    f"SiteSettings.site_name would collapse to a single-letter automatic monogram ('{monogram}'). "
                    "Set nav_name or upload a logo before launch."
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

    if not getattr(django_settings, "CONTACT_EMAIL", "").strip():
        warnings.append(
            "CONTACT_EMAIL is blank. Public contact details may still render, but contact-form notification emails "
            "will not reach the practice until the internal inbox is configured in the environment."
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
    elif stale_brand := _stale_meta_brand(site.about_meta_description, site.site_name):
        blockers.append(
            f"SiteSettings.about_meta_description still references '{stale_brand}', "
            f"which does not match the current site name ('{site.site_name}'). "
            "Update it or clear the field to fall back to the homepage meta description."
        )

    if not site.services_meta_description:
        warnings.append(
            "SiteSettings.services_meta_description is blank. "
            "The Services page will fall back to the homepage meta description."
        )
    elif stale_brand := _stale_meta_brand(site.services_meta_description, site.site_name):
        blockers.append(
            f"SiteSettings.services_meta_description still references '{stale_brand}', "
            f"which does not match the current site name ('{site.site_name}'). "
            "Update it or clear the field to fall back to the homepage meta description."
        )

    if not site.projects_meta_description:
        warnings.append(
            "SiteSettings.projects_meta_description is blank. "
            "The Projects page will fall back to the homepage meta description."
        )
    elif stale_brand := _stale_meta_brand(site.projects_meta_description, site.site_name):
        blockers.append(
            f"SiteSettings.projects_meta_description still references '{stale_brand}', "
            f"which does not match the current site name ('{site.site_name}'). "
            "Update it or clear the field to fall back to the homepage meta description."
        )

    if not site.contact_meta_description:
        warnings.append(
            "SiteSettings.contact_meta_description is blank. "
            "The Contact page will fall back to the homepage meta description."
        )
    elif stale_brand := _stale_meta_brand(site.contact_meta_description, site.site_name):
        blockers.append(
            f"SiteSettings.contact_meta_description still references '{stale_brand}', "
            f"which does not match the current site name ('{site.site_name}'). "
            "Update it or clear the field to fall back to the homepage meta description."
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

    if not public_text(about.practice_structure):
        warnings.append(
            "AboutProfile.practice_structure is omitted or still a starter prompt. "
            "The About hero will hide this line until real practice-structure wording is available."
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

    if not public_text(about.project_leadership):
        warnings.append(
            "AboutProfile.project_leadership is omitted or still a starter prompt. "
            "The About page will hide this section until real project-leadership wording is available."
        )
    elif about.project_leadership == _DEMO_ABOUT_PROJECT_LEADERSHIP:
        blockers.append(
            "AboutProfile.project_leadership is still demo/reference copy. "
            "Replace it with your real project leadership statement."
        )

    if not public_text(about.professional_standing):
        warnings.append(
            "AboutProfile.professional_standing is omitted or still a starter prompt. "
            "The public professional-profile block will stay hidden until exact standing wording is available."
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
        homepage_projects_desktop_count = site.homepage_projects_desktop_count
        featured_projects = list(
            Project.objects.with_preview_media()
            .filter(featured=True)
            .order_by("order")[:homepage_projects_desktop_count]
        )
        homepage_projects = featured_projects or list(
            Project.objects.with_preview_media()
            .order_by("order")[:homepage_projects_desktop_count]
        )

        if not featured_projects:
            warnings.append(
                "No featured Project records are selected. "
                "The homepage will fall back to the first ordered projects until featured projects are chosen."
            )

        hero_project = homepage_projects[0] if homepage_projects else None
        if hero_project and not hero_project.cover_image:
            warnings.append(
                f"The current homepage hero project ('{hero_project.title}') has no cover image. "
                "The hero will use the placeholder background until a cover image is uploaded or a different project is chosen first."
            )

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
        "before launch. Exits with code 1 if any blocking launch issues are reported."
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
