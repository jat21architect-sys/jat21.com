"""
Management command: python manage.py seed_demo

Seeds a complete set of generic starter content: SiteSettings, AboutProfile,
Services, and placeholder projects so the site renders immediately after setup.

This is your starting point — use it to see a working site, then replace
content with your own via the admin. All copy uses generic placeholders;
nothing is specific to any individual or region.

Idempotent — safe to re-run (uses get_or_create / update, duplicate detection
for cover images and gallery images).

Optional flag
-------------
  --media-dir PATH   Attach demo media from a local folder.

Expected layout under PATH
--------------------------
  portrait.*
  covers/
    house-on-the-hillside.*
    commercial-office-conversion.*
  gallery/
    community-library-pavilion/
      01.*  02.*  03.*
    commercial-office-conversion/
      01.*  02.*  03.*

Supported extensions: .jpg .jpeg .png .webp (case-insensitive).
Missing individual files warn and continue; an invalid PATH errors immediately.
"""

import os
import re
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.core.models import AboutProfile, SiteSettings
from apps.projects.models import Project, ProjectImage, Testimonial
from apps.services.models import Service

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# Strips Django collision-avoidance suffixes, e.g. "cover_vFlUiiN" → "cover"
_DJANGO_SUFFIX_RE = re.compile(r"_[A-Za-z0-9]{7}$")


def _stem_clean(name: str) -> str:
    stem = Path(name).stem
    return _DJANGO_SUFFIX_RE.sub("", stem)


def _find_file(directory: Path, stem: str) -> Path | None:
    """Return the first file in *directory* whose stem matches *stem* (any supported ext)."""
    for ext in _IMAGE_EXTS:
        candidate = directory / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    return None


def _list_images(directory: Path) -> list[Path]:
    """Return sorted image files in *directory* (non-recursive)."""
    found = sorted(
        p for p in directory.iterdir()
        if p.is_file() and p.suffix.lower() in _IMAGE_EXTS
    )
    return found

SERVICES = [
    {
        "title": "Architectural Design",
        "summary": "Full architectural services from first sketch to planning submission and construction.",
        "description": (
            "Complete end-to-end architectural design covering brief development, "
            "concept design, developed design, technical documentation, planning "
            "application, building regulations, and construction administration."
        ),
        "who_for": "Private clients, developers, property owners planning new builds or significant extensions.",
        "value_proposition": "A design partner through every stage — ensuring spatial quality, regulatory compliance, and delivery within brief.",
        "deliverables": "Concept sketches and diagrams\nDeveloped design drawings\nPlanning and building regulations submissions\nConstruction drawings and specifications\nSite visit reports",
        "order": 1,
    },
    {
        "title": "Residential Design",
        "summary": "Thoughtful homes designed around the way people live — from family houses to urban apartments.",
        "description": (
            "Residential architecture requires a deep understanding of how people inhabit "
            "space. Every project begins with listening — to the client's life, aspirations, "
            "and the specific character of the site — before any line is drawn."
        ),
        "who_for": "Families, individuals, and developers seeking residential design with genuine character and spatial quality.",
        "value_proposition": "Homes that are both beautiful and practical — designed to last and to grow with the people who live in them.",
        "deliverables": "Site and brief analysis\nConcept design options\nFull architectural drawings\nInterior layout and specification",
        "order": 2,
    },
    {
        "title": "Concept Development",
        "summary": "Strategic early-stage design thinking to establish direction, test ideas, and build confidence before committing to full development.",
        "description": (
            "The concept stage is where the most important decisions are made. "
            "This service provides rigorous early-stage design exploration — "
            "spatial strategy, massing studies, precedent research, and a clearly "
            "communicated design direction ready for next steps."
        ),
        "who_for": "Clients at the early stages of a project who need clarity before engaging a full design team.",
        "value_proposition": "Reduce risk, sharpen brief, and arrive at a defensible design direction before significant investment.",
        "deliverables": "Spatial strategy document\nConcept diagrams and sketches\nMassing and site studies\nDesign direction presentation",
        "order": 3,
    },
    {
        "title": "Renovation & Adaptive Reuse",
        "summary": "Transforming existing buildings with care, intelligence, and respect for their character and history.",
        "description": (
            "Existing buildings contain value — structural, material, contextual, and cultural. "
            "Renovation and adaptive reuse projects require a particular kind of design "
            "intelligence: the ability to read what is already there, identify what must be "
            "preserved, and find the precise interventions that unlock new life."
        ),
        "who_for": "Property owners, developers, and institutions working with existing buildings of any age.",
        "value_proposition": "A more sustainable approach that maximises the value of what exists while creating spaces fit for today's needs.",
        "deliverables": "Existing building survey and analysis\nConservation statement if required\nRenovation design package\nMaterials and finishes specification",
        "order": 4,
    },
    {
        "title": "Interior Architecture",
        "summary": "Interior environments designed with the same rigour and spatial intelligence as the architecture itself.",
        "description": (
            "Interior architecture is not decoration — it is the design of space from the "
            "inside out. Light, proportion, material, sequence, and detail combine to create "
            "interiors that feel considered, coherent, and specific to their purpose and occupant."
        ),
        "who_for": "Clients seeking interior design that is architecturally considered, not trend-led.",
        "value_proposition": "Interiors with lasting quality — spatial logic, material integrity, and a clear design language.",
        "deliverables": "Interior layout and spatial design\nMaterials and finishes palette\nLighting concept\nFurniture and fitout coordination",
        "order": 5,
    },
    {
        "title": "Design Consultation",
        "summary": "Expert architectural advice for projects at any stage — planning, design review, feasibility, or procurement.",
        "description": (
            "Not every project requires a full architectural appointment. Sometimes what "
            "is needed is the perspective of an experienced architect to review options, "
            "assess feasibility, challenge assumptions, or provide a second opinion."
        ),
        "who_for": "Clients, developers, and other consultants who need focused expert input without a full commission.",
        "value_proposition": "Clear, honest architectural advice that adds value quickly and reduces costly mistakes.",
        "deliverables": "Consultation report\nFeasibility assessment\nDesign review notes\nRecommendations and next steps",
        "order": 6,
    },
]

PROJECTS = [
    {
        "slug": "house-on-the-hillside",
        "title": "House on the Hillside",
        "short_description": "A private residence that uses the natural topography of its sloping site to create a sequence of connected levels, each framing a distinct view of the landscape.",
        "category": "housing",
        "status": "completed",
        "location": "Hillside Region",
        "year": 2023,
        "area": "320 m²",
        "overview": "Set on a steeply sloping site at the edge of a small town, this private house uses the natural fall of the land to organise a sequence of living levels — each with its own relationship to the landscape and light. The brief called for a family home that would feel rooted in its place, generous without excess, and quietly contemporary in character.",
        "challenge": "The site presented both an opportunity and a constraint. The slope made conventional construction expensive, but it also offered the possibility of layering the programme vertically — allowing each space to find its own horizon. The challenge was to use this sectional complexity architecturally rather than treating it as a problem to overcome.",
        "concept": "The design concept resolves around a single spine wall that runs parallel to the contours and anchors the building to the hillside. From this wall, a series of platforms step down the slope — living above, sleeping below, landscape everywhere. Each level is connected by a continuous internal stair that also functions as the organisational core of the house.",
        "outcome": "The completed house feels both specific to its site and quietly universal in its spatial logic. The clients describe it as a home that feels larger than its footprint because every room opens directly to the outside.",
        "featured": True,
        "order": 1,
    },
    {
        "slug": "community-library-pavilion",
        "title": "Community Library Pavilion",
        "short_description": "A lightweight civic pavilion housing a branch library, reading rooms, and flexible community space — designed to be both a landmark and a welcoming public threshold.",
        "category": "civic",
        "status": "completed",
        "location": "Coastal City",
        "year": 2022,
        "area": "480 m²",
        "overview": "This community library pavilion was commissioned by a local municipality as part of a small civic precinct development. The brief asked for a building that would serve the neighbourhood as a library, study space, and informal gathering place — one that would feel welcoming even to those who had never entered a library before.",
        "challenge": "Public libraries often fail because they are over-designed as monuments or under-designed as pragmatic sheds. The challenge here was to make a building that was distinct enough to be a destination while remaining genuinely open and non-intimidating — a threshold between the street and a place of quiet.",
        "concept": "The pavilion is organised around a central covered courtyard — an in-between space that is neither inside nor outside — from which all other rooms are reached. The roof structure is a lightweight timber frame that filters light without enclosing it. The building makes no grand gestures; its civic presence comes from its quality of light, material, and the generosity of its threshold.",
        "outcome": "The pavilion has become a well-used public space. Usage data from the first year showed significantly higher visitor numbers than comparable libraries in the region. The courtyard has been informally adopted as an after-school gathering space.",
        "featured": True,
        "order": 2,
    },
    {
        "slug": "urban-apartment-retrofit",
        "title": "Urban Apartment Retrofit",
        "short_description": "The interior transformation of a 1970s apartment block unit — stripping back decades of poor alterations to reveal strong bones and reorganise the plan for contemporary urban living.",
        "category": "housing",
        "status": "completed",
        "location": "City Centre",
        "year": 2024,
        "area": "95 m²",
        "overview": "A compact city apartment — the kind that had been subdivided and re-divided over five decades — was stripped back to its structure and completely reimagined. The starting point was a question: what is actually here, and what should be here?",
        "challenge": "Years of minor alterations had obscured the apartment's original logic and left it a sequence of poorly proportioned, poorly lit rooms. The challenge was to recover the spatial potential within a fixed building envelope — and to do so on a limited renovation budget.",
        "concept": "The design consolidates circulation to free up living, creates a contained kitchen core that frees the main space entirely, and uses a consistent material language — white plaster, dark-stained timber, exposed concrete — to give the apartment coherence and a sense of deliberateness it had never had.",
        "outcome": "The apartment now reads as a confident, well-proportioned urban dwelling. The living area, which previously felt fragmented, now functions as a single continuous room with direct daylight from two aspects.",
        "featured": False,
        "order": 3,
    },
    {
        "slug": "commercial-office-conversion",
        "title": "Commercial Office Conversion",
        "short_description": "The transformation of a decommissioned warehouse into a flexible co-working campus — preserving industrial character while introducing contemporary amenity and environmental performance.",
        "category": "workplace",
        "status": "completed",
        "location": "City District",
        "year": 2023,
        "client": "Undisclosed Property Developer",
        "area": "1 850 m²",
        "overview": (
            "A former textile warehouse in the inner city was acquired for conversion into a "
            "mixed-tenancy workspace. The brief asked for a building that would appeal to "
            "creative businesses and technology companies while generating a viable return for "
            "the developer across a range of unit sizes."
        ),
        "challenge": (
            "The warehouse structure — heavy masonry walls, timber roof frames, concrete floors — "
            "was both an asset and a constraint. The existing grid did not map neatly onto "
            "contemporary workspace metrics, and the building's deep plan made natural daylighting "
            "across all zones a genuine challenge."
        ),
        "concept": (
            "The design introduces a central atrium carved from the building's footprint — a "
            "void that brings daylight to the plan's interior and becomes the social spine of "
            "the building. Tenancies are arranged as a series of gallery-style units around this "
            "atrium, each with a mezzanine level that doubles usable floor area without increasing "
            "the building's footprint or height."
        ),
        "process": (
            "The project proceeded in two phases: shell-and-core works completed under a single "
            "contract, with fitout elements designed and delivered tenant-by-tenant as the "
            "building filled. This phased approach allowed the design to respond to occupants' "
            "specific needs while maintaining the coherence of the overall architectural language."
        ),
        "outcome": (
            "The building reached full occupancy within fourteen months of completion — faster "
            "than comparable conversions in the area. The atrium has become an informal event "
            "space used regularly by tenants and has been featured in regional architecture and "
            "property media."
        ),
        "featured": True,
        "order": 4,
    },
]

TESTIMONIALS = [
    {
        "name": "Sarah & Mark L.",
        "role": "Private Clients",
        "company": "",
        "quote": (
            "Working with the studio was the best decision we made on this project. "
            "They listened carefully from the very first meeting, never tried to impose "
            "a signature style, and kept us informed at every stage. The house exceeded "
            "what we thought was possible on our budget and timeline."
        ),
        "project_slug": "house-on-the-hillside",
        "order": 1,
    },
    {
        "name": "A. Navarro",
        "role": "Municipal Library Director",
        "company": "City District Municipality",
        "quote": (
            "The pavilion has transformed how the community uses the library. We were "
            "worried a striking building might feel intimidating — the opposite happened. "
            "The quality of the space seems to put people at ease. Usage numbers in the "
            "first year were double our projections."
        ),
        "project_slug": "community-library-pavilion",
        "order": 2,
    },
    {
        "name": "C. Brennan",
        "role": "Director of Acquisitions",
        "company": "Urban Property Group",
        "quote": (
            "The studio delivered a technically complex project on time and within budget, "
            "which alone would make them stand out. But the commercial outcome — full "
            "occupancy inside fourteen months — reflects design quality as much as market "
            "conditions. We will work with them again."
        ),
        "project_slug": "commercial-office-conversion",
        "order": 3,
    },
]


class Command(BaseCommand):
    help = (
        "Seed generic starter content: SiteSettings, AboutProfile, Services, and example "
        "Projects with placeholder testimonials. Use as your starting point and replace "
        "content via admin. Idempotent — safe to re-run."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--media-dir",
            metavar="PATH",
            default=None,
            help=(
                "Attach demo media from this directory. "
                "Expected layout: portrait.*, covers/<slug>.*, gallery/<slug>/*.* "
                "Supported extensions: .jpg .jpeg .png .webp"
            ),
        )

    def handle(self, *args, **options):
        media_dir: Path | None = None
        if options["media_dir"]:
            media_dir = Path(options["media_dir"]).resolve()
            if not media_dir.is_dir():
                raise CommandError(f"--media-dir does not exist or is not a directory: {media_dir}")

        self._seed_settings()
        self._seed_about()
        self._seed_services()
        self._seed_projects()
        self._seed_testimonials()

        # ---------- media attachment ----------
        portrait_attached = False
        covers_attached = 0
        gallery_attached = 0
        warnings_count = 0

        if media_dir:
            portrait_attached, portrait_warns = self._attach_portrait(media_dir)
            warnings_count += portrait_warns

            c, c_warns = self._attach_covers(media_dir)
            covers_attached = c
            warnings_count += c_warns

            g, g_warns = self._attach_galleries(media_dir)
            gallery_attached = g
            warnings_count += g_warns

            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_HEADING("Media summary:"))
            self.stdout.write(f"  portrait attached : {'yes' if portrait_attached else 'no'}")
            self.stdout.write(f"  covers attached   : {covers_attached}")
            self.stdout.write(f"  gallery images    : {gallery_attached}")
            self.stdout.write(f"  warnings          : {warnings_count}")

        self.stdout.write(self.style.SUCCESS("\nStarter content seeded successfully."))

    # ------------------------------------------------------------------
    # Text content seeders
    # ------------------------------------------------------------------

    def _seed_settings(self):
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        settings.site_name = "Demo Architecture Studio"
        settings.tagline = "Architectural design shaped by context, clarity, and identity."
        settings.contact_email = "hello@demo-architecture.example"
        settings.location = "Your City, Your Country"
        settings.meta_description = (
            "An architecture practice whose work combines spatial clarity, "
            "contextual sensitivity, and thoughtful design to create places with identity, "
            "purpose, and lasting value."
        )
        settings.save()
        action = "Created" if created else "Updated"
        self.stdout.write(f"  {action} SiteSettings")

    def _seed_about(self):
        profile, created = AboutProfile.objects.get_or_create(pk=1)
        profile.identity_mode = AboutProfile.IdentityMode.STUDIO
        profile.principal_name = ""
        profile.principal_title = ""
        profile.practice_structure = "Independent architecture studio"
        profile.one_line_practice_description = (
            "Architecture shaped by context, use, and urban climate."
        )
        profile.practice_summary = (
            "Demo Architecture Studio is a practice working across housing, civic buildings, "
            "and workplace projects in northern urban settings. The work is defined by clear "
            "massing, durable materials, careful daylighting, and legible circulation.\n\n"
            "The studio works on projects that sit between everyday infrastructure and long-term "
            "city-making: housing blocks, public buildings, workplaces, and mixed-use urban sites. "
            "Rather than treating architecture as image-making, the emphasis is on performance, "
            "clarity, and how buildings hold up over time."
        )
        profile.project_leadership = (
            "Projects are led by a compact studio team, with specialist consultants involved as "
            "needed for structure, building services, and planning coordination."
        )
        profile.professional_standing = "Registered architectural practice"
        profile.education = (
            "Bachelor of Architecture (Professional)\n"
            "Master of Architecture"
        )
        profile.supporting_facts = (
            "Housing, civic, and workplace project experience\n"
            "Planning, technical design, and consultant coordination\n"
            "New-build and urban infill commissions"
        )
        profile.approach = (
            "Buildings in northern settings need to manage weather, frame daylight carefully, "
            "and make circulation feel intuitive in difficult conditions.\n\n"
            "The work focuses on fit rather than spectacle: how a building sits in context, "
            "how structure and envelope reinforce one another, and how public or shared spaces "
            "are made legible through proportion and movement."
        )
        profile.experience_years = 12
        profile.closing_invitation = (
            "Get in touch with a short outline of your project, whether the brief is developed "
            "or still taking shape."
        )
        profile.portrait_mode = AboutProfile.PortraitMode.TEXT_ONLY
        profile.save()
        action = "Created" if created else "Updated"
        self.stdout.write(f"  {action} AboutProfile")

    def _seed_services(self):
        for data in SERVICES:
            obj, created = Service.objects.get_or_create(title=data["title"])
            for key, value in data.items():
                if key != "title":
                    setattr(obj, key, value)
            obj.save()
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} Service: {obj.title}")

    def _seed_projects(self):
        for data in PROJECTS:
            slug = data["slug"]
            obj, created = Project.objects.get_or_create(slug=slug, defaults={"title": data["title"]})
            for key, value in data.items():
                if key != "slug":
                    setattr(obj, key, value)
            obj.save()
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} Project: {obj.title} (slug={obj.slug})")

    def _seed_testimonials(self):
        for data in TESTIMONIALS:
            project_slug = data.get("project_slug")
            project = None
            if project_slug:
                project = Project.objects.filter(slug=project_slug).first()
            obj, created = Testimonial.objects.get_or_create(
                name=data["name"],
                defaults={"project": project},
            )
            for key, value in data.items():
                if key not in ("name", "project_slug"):
                    setattr(obj, key, value)
            obj.project = project
            obj.save()
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} Testimonial: {obj.name}")

    # ------------------------------------------------------------------
    # Media attachment helpers
    # ------------------------------------------------------------------

    def _warn(self, msg: str) -> int:
        self.stdout.write(self.style.WARNING(f"  WARNING: {msg}"))
        return 1

    def _attach_portrait(self, media_dir: Path) -> tuple[bool, int]:
        """Attach portrait.* to AboutProfile. Returns (attached, warning_count)."""
        portrait_file = _find_file(media_dir, "portrait")
        if not portrait_file:
            w = self._warn(f"portrait.* not found in {media_dir}")
            return False, w

        profile = AboutProfile.objects.get_or_create(pk=1)[0]
        # Skip if same file already attached
        if profile.portrait and _stem_clean(profile.portrait.name) == _stem_clean(portrait_file.name):
            self.stdout.write(f"  SKIP portrait (already attached): {portrait_file.name}")
            return True, 0

        with portrait_file.open("rb") as fh:
            profile.portrait.save(portrait_file.name, File(fh), save=True)
        profile.portrait_mode = AboutProfile.PortraitMode.PORTRAIT
        profile.save(update_fields=["portrait_mode"])
        self.stdout.write(f"  Attached portrait → {profile.portrait.name}")
        return True, 0

    def _attach_covers(self, media_dir: Path) -> tuple[int, int]:
        """Attach covers for the projects that should have one.
        Returns (count_attached_or_skipped, warning_count)."""
        covers_dir = media_dir / "covers"
        attached = 0
        warnings = 0
        cover_slugs = ["house-on-the-hillside", "commercial-office-conversion"]

        for slug in cover_slugs:
            cover_file = _find_file(covers_dir, slug) if covers_dir.is_dir() else None
            if cover_file is None:
                path_hint = covers_dir / slug
                warnings += self._warn(f"cover not found: {path_hint}.*")
                continue

            try:
                project = Project.objects.get(slug=slug)
            except Project.DoesNotExist:
                warnings += self._warn(f"Project with slug '{slug}' not found — skipping cover")
                continue

            # Skip if same file already attached
            if (
                project.cover_image
                and _stem_clean(project.cover_image.name) == _stem_clean(cover_file.name)
            ):
                self.stdout.write(f"  SKIP cover for '{slug}' (already attached): {cover_file.name}")
                attached += 1
                continue

            with cover_file.open("rb") as fh:
                project.cover_image.save(cover_file.name, File(fh), save=True)
            self.stdout.write(f"  Attached cover for '{slug}' → {project.cover_image.name}")
            attached += 1

        return attached, warnings

    def _attach_galleries(self, media_dir: Path) -> tuple[int, int]:
        """Attach gallery images for the projects that should have them.
        Returns (count_new_images_added, warning_count)."""
        gallery_dir = media_dir / "gallery"
        total_added = 0
        warnings = 0
        gallery_slugs = ["community-library-pavilion", "commercial-office-conversion"]

        for slug in gallery_slugs:
            project_gallery_dir = gallery_dir / slug if gallery_dir.is_dir() else Path("/nonexistent")
            if not project_gallery_dir.is_dir():
                warnings += self._warn(f"gallery directory not found: {project_gallery_dir}")
                continue

            image_files = _list_images(project_gallery_dir)
            if not image_files:
                warnings += self._warn(f"no images found in {project_gallery_dir}")
                continue

            try:
                project = Project.objects.get(slug=slug)
            except Project.DoesNotExist:
                warnings += self._warn(f"Project with slug '{slug}' not found — skipping gallery")
                continue

            # Build set of already-stored stems for duplicate detection
            existing_stems = {
                _stem_clean(os.path.basename(img.image.name))
                for img in project.images.all()
                if img.image.name
            }
            next_order = (
                project.images.order_by("-order").values_list("order", flat=True).first() or 0
            ) + 1

            added = 0
            for img_path in image_files:
                if _stem_clean(img_path.name) in existing_stems:
                    self.stdout.write(f"  SKIP gallery image (duplicate): {img_path.name}")
                    continue
                with img_path.open("rb") as fh:
                    img_obj = ProjectImage(
                        project=project,
                        order=next_order,
                        image_type="gallery",
                    )
                    img_obj.image.save(img_path.name, File(fh), save=True)
                next_order += 1
                added += 1
                self.stdout.write(f"  Attached gallery image for '{slug}': {img_path.name}")

            total_added += added

        return total_added, warnings
