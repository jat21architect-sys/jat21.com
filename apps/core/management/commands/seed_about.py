"""
Management command: seed_about
-------------------------------
Populates the AboutProfile singleton with buyer-safe starter prompts.

By default, only fills fields that are currently blank — so admin edits
made after the first run are preserved.

Usage:
    uv run python manage.py seed_about            # fill blank fields only
    uv run python manage.py seed_about --force    # overwrite all text fields

Fields NOT set by this command (must be set in admin):
    - identity_mode      (choose person-led or studio-led if the default is wrong)
    - principal_name     (required for person-led practices)
    - principal_title    (required for person-led practices)
    - experience_years   (enter your real number)
    - portrait           (upload file if using portrait mode)
    - cv_file            (upload file if genuinely useful)
    - site location      (set in admin → Site Settings)

Run on production via Railway:
    railway run python manage.py seed_about
"""

from django.core.management.base import BaseCommand

from apps.core.about_defaults import (
    CLOSING_INVITATION_DEFAULT,
    PRACTICE_STRUCTURE_PROMPT,
    PROFESSIONAL_STANDING_PROMPT,
    PROJECT_LEADERSHIP_PROMPT,
)
from apps.core.models import AboutProfile

CONTENT = {
    "practice_structure": PRACTICE_STRUCTURE_PROMPT,
    "one_line_practice_description": (
        "[Add a one-line public description of the practice]"
    ),
    "practice_summary": (
        "[Describe what the practice does, where it is based, and the kinds of projects it takes on.]"
    ),
    "project_leadership": PROJECT_LEADERSHIP_PROMPT,
    "professional_standing": PROFESSIONAL_STANDING_PROMPT,
    "education": (
        "[Add education details, one per line]"
    ),
    "supporting_facts": (
        "[Add at least one concrete supporting fact, one per line]"
    ),
    "approach": (
        "[Add a short practical approach statement in 2 to 3 sentences.]"
    ),
    "closing_invitation": CLOSING_INVITATION_DEFAULT,
}

TEXT_FIELDS = list(CONTENT.keys())


class Command(BaseCommand):
    help = "Seed AboutProfile with buyer-safe starter prompts (blank fields only by default)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite all text fields, even if already populated.",
        )

    def handle(self, *args, **options):
        profile = AboutProfile.load()
        force = options["force"]

        updated = []
        skipped = []

        for field, value in CONTENT.items():
            current = getattr(profile, field, "")
            if force or not current.strip():
                setattr(profile, field, value)
                updated.append(field)
            else:
                skipped.append(field)

        if updated:
            profile.save()
            self.stdout.write(self.style.SUCCESS(f"Updated fields: {', '.join(updated)}"))
        else:
            self.stdout.write("No fields updated — all already populated.")

        if skipped:
            self.stdout.write(f"Skipped (already populated): {', '.join(skipped)}")

        self.stdout.write(
            self.style.WARNING(
                "\nRemember to set in admin: identity_mode, principal_name/title if needed, "
                "experience_years, portrait_mode, portrait, cv_file, and Site Settings location"
            )
        )
