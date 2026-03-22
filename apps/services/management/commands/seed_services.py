"""
Management command: seed_services
----------------------------------
Creates the initial set of Service records for the live site.

Usage:
    uv run python manage.py seed_services           # create only (skip existing)
    uv run python manage.py seed_services --reset   # delete all services, then create

Run on production via Railway:
    railway run python manage.py seed_services
"""

from django.core.management.base import BaseCommand

from apps.services.models import Service

SERVICES = [
    {
        "title": "Residential Design",
        "slug": "residential-design",
        "summary": (
            "New homes, extensions, and outbuildings — "
            "designed from site analysis through to construction documentation."
        ),
        "description": "",
        "who_for": (
            "Homeowners planning a new build, extension, or outbuilding on "
            "an existing property."
        ),
        "value_proposition": (
            "A complete design that responds to your site, your programme, and "
            "your budget — developed with enough detail to build from with confidence."
        ),
        "deliverables": (
            "Site and context analysis\n"
            "Concept design options\n"
            "Design development drawings\n"
            "Construction documentation\n"
            "Local authority submission package"
        ),
        "order": 1,
        "active": True,
    },
    {
        "title": "Renovation & Adaptive Reuse",
        "slug": "renovation-adaptive-reuse",
        "summary": (
            "Existing buildings brought up to date — restructured, extended, "
            "or repurposed without losing what makes them worth keeping."
        ),
        "description": "",
        "who_for": (
            "Owners of existing buildings that need structural, spatial, or "
            "functional improvement — including heritage-adjacent work."
        ),
        "value_proposition": (
            "A considered design process that works with the existing structure "
            "rather than against it, identifying the right interventions "
            "for the right reasons."
        ),
        "deliverables": (
            "Condition and feasibility assessment\n"
            "Design proposals with phasing options\n"
            "Construction documentation"
        ),
        "order": 2,
        "active": True,
    },
    {
        "title": "Interior Architecture",
        "slug": "interior-architecture",
        "summary": (
            "Interior spatial design for residential and selected commercial "
            "projects — from layout and materiality through to specification."
        ),
        "description": "",
        "who_for": (
            "Clients who have a shell or existing space and need the interior "
            "resolved with the same rigour as the architecture."
        ),
        "value_proposition": (
            "Interior design that is spatially coherent, "
            "not decorative — built on the same thinking as the architecture."
        ),
        "deliverables": (
            "Spatial layout and planning\n"
            "Materials and finishes schedule\n"
            "Joinery and fixture design\n"
            "Specification drawings"
        ),
        "order": 3,
        "active": True,
    },
    {
        "title": "Concept Design",
        "slug": "concept-design",
        "summary": (
            "Early-stage design thinking for projects that are not yet fully "
            "defined — to test feasibility, establish direction, and sharpen the brief."
        ),
        "description": "",
        "who_for": (
            "Clients with a site or rough idea who need help testing what is "
            "possible before committing to a full design process."
        ),
        "value_proposition": (
            "A clear, documented concept that gives you something concrete to "
            "take to a bank, planning authority, or building committee — "
            "and a stronger brief to proceed with."
        ),
        "deliverables": (
            "Site feasibility study\n"
            "Concept sketches and diagrams\n"
            "Programme outline\n"
            "Summary report"
        ),
        "order": 4,
        "active": True,
    },
]


class Command(BaseCommand):
    help = "Seed the initial set of Service records."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing Service records before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = Service.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing service(s)."))

        created = 0
        skipped = 0
        for data in SERVICES:
            _, was_created = Service.objects.get_or_create(
                slug=data["slug"],
                defaults=data,
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — {created} service(s) created, {skipped} already existed."
            )
        )
