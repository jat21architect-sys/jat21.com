"""
Management command: seed_about
-------------------------------
Populates the AboutProfile singleton with real, client-facing content.

By default, only fills fields that are currently blank — so admin edits
made after the first run are preserved.

Usage:
    uv run python manage.py seed_about            # fill blank fields only
    uv run python manage.py seed_about --force    # overwrite all text fields

Fields NOT set by this command (must be set in admin):
    - experience_years  (specific to Jeannot — enter the real number)
    - portrait          (upload file)
    - cv_file           (upload file)
    - location          (set to city/region as appropriate)

Run on production via Railway:
    railway run python manage.py seed_about
"""

from django.core.management.base import BaseCommand

from apps.core.models import AboutProfile

CONTENT = {
    "headline": (
        "Architect working across residential design, renovation, and interior architecture."
    ),
    "intro": (
        "Jeannot Tsirenge is a registered architect based in South Africa, working with "
        "private clients on residential projects, renovations, and interior architecture. "
        "His practice focuses on work that is grounded in site, brief, and budget — "
        "designed with enough specificity to build well. "
        "Whether the project is a new home, an existing building being restructured, "
        "or an interior resolved from first principles, the approach is the same: "
        "understand the problem clearly before proposing the answer."
    ),
    "biography": (
        "I work with clients who want to build something considered — not necessarily "
        "complex or expensive, but designed with real attention to the particulars of "
        "the site, the programme, and the people using the space.\n\n"
        "Most of my work is residential: new homes, extensions, alterations, and "
        "interior architecture for private clients. I also take on selected renovation "
        "and adaptive reuse projects where the existing building offers something "
        "worth working with.\n\n"
        "My approach to each project begins with questions before it begins with "
        "drawings — understanding the site, the constraints, and what the client "
        "actually needs, rather than what a brief initially says. A client who has "
        "already thought through the practical questions of their project will find "
        "the process moves quickly and reduces waste. A client who is still working "
        "through the first questions will find the same process helps them shape "
        "a clearer brief."
    ),
    "philosophy": (
        "Good architecture is specific. It responds to the actual conditions of the "
        "site, the way people use space, and the budget available — not to a general "
        "theory about what buildings should look like.\n\n"
        "My process starts with constraints, not precedents. Before anything goes on "
        "paper, I want to understand the boundaries we are working within: planning "
        "rules, structural realities, budget, construction sequence. Those constraints "
        "are not problems to be overcome — they are the material the design is made from.\n\n"
        "I work closely with clients through each stage, keeping the process legible "
        "and decisions explicit. The goal is that nothing on site surprises anyone — "
        "and that the client understands why each decision was made, not just what "
        "was decided."
    ),
}

TEXT_FIELDS = list(CONTENT.keys())


class Command(BaseCommand):
    help = "Seed AboutProfile with client-facing content (blank fields only by default)."

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
                "\nRemember to set in admin: experience_years, location, portrait, cv_file"
            )
        )
