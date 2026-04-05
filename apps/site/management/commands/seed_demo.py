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

from apps.projects.models import Project, ProjectImage, Testimonial
from apps.services.models import Service
from apps.site.models import AboutProfile, SiteSettings

_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# Strips Django collision-avoidance suffixes, e.g. "cover_vFlUiiN" → "cover"
_DJANGO_SUFFIX_RE = re.compile(r"_[A-Za-z0-9]{7}$")


def _stem_clean(name: str | None) -> str:
    if not name:
        return ""
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


def _discover_demo_media_dir(media_root: Path) -> Path | None:
    """Return the first bundled demo-media directory that exists."""
    candidates = [
        Path(__file__).resolve().parents[2] / "demo_seed" / "strand-architecture",
        media_root / "demo_seed" / "strand-architecture",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


DEMO_COVER_SOURCES = {
    "coastline-civic-centre": "covers/coastline-civic-centre.jpg",
    "harbour-court-apartments": "covers/harbour-court-apartments.jpg",
    "harbour-glass-offices": "covers/harbour-glass-offices.jpg",
    "ridgeline-housing": "covers/ridgeline-housing.jpg",
    "school-extension-timber-frame": "covers/school-extension-timber-frame.jpg",
    "urban-apartment-retrofit": "covers/urban-apartment-retrofit.jpg",
    "house-on-the-hillside": "gallery/ridgeline-housing/01.jpg",
    "community-library-pavilion": "gallery/coastline-civic-centre/01.jpg",
    "commercial-office-conversion": "covers/harbour-glass-offices.jpg",
    "civic-waterfront-square": "gallery/coastline-civic-centre/02.jpg",
    "housing-block-north-quarter": "gallery/harbour-court-apartments/01.jpg",
}

DEMO_GALLERY_SOURCES = {
    "coastline-civic-centre": [
        "gallery/coastline-civic-centre/01.jpg",
        "gallery/coastline-civic-centre/02.jpg",
        "gallery/coastline-civic-centre/03.jpg",
        "gallery/coastline-civic-centre/04.jpg",
    ],
    "harbour-court-apartments": [
        "gallery/harbour-court-apartments/01.jpg",
        "gallery/harbour-court-apartments/02.jpg",
        "gallery/harbour-court-apartments/03.jpg",
        "gallery/harbour-court-apartments/04.jpg",
        "gallery/harbour-court-apartments/05.jpg",
    ],
    "ridgeline-housing": [
        "gallery/ridgeline-housing/01.jpg",
        "gallery/ridgeline-housing/02.jpg",
        "gallery/ridgeline-housing/03.jpg",
        "gallery/ridgeline-housing/04.jpg",
        "gallery/ridgeline-housing/05.jpg",
        "gallery/ridgeline-housing/06.jpg",
        "gallery/ridgeline-housing/07.jpg",
    ],
    "house-on-the-hillside": [
        "gallery/ridgeline-housing/02.jpg",
        "gallery/ridgeline-housing/03.jpg",
        "gallery/ridgeline-housing/04.jpg",
        "gallery/ridgeline-housing/05.jpg",
    ],
}

SERVICES = [
    {
        "title": "Housing",
        "slug": "housing",
        "summary": "Apartment buildings, housing blocks, and residential projects designed for clear planning, durable use, and long-term liveability.",
        "description": "",
        "who_for": "Developers, housing associations, institutions, and private clients delivering apartment buildings, infill housing, or residential work.",
        "value_proposition": "Clear housing design that balances site conditions, planning constraints, and day-to-day use without overstatement.",
        "deliverables": "Site and massing studies\nPlanning package\nDeveloped design\nTechnical coordination\nConstruction information",
        "order": 1,
    },
    {
        "title": "Civic",
        "slug": "civic",
        "summary": "Public-facing buildings shaped by threshold, circulation, durability, and a clear relationship between civic use and context.",
        "description": "",
        "who_for": "Municipal bodies, trusts, cultural organisations, and public-sector clients commissioning libraries, community facilities, and civic buildings.",
        "value_proposition": "Buildings that support everyday public use with clarity, resilience, and a calm architectural presence.",
        "deliverables": "Brief development\nConcept design\nPublic consultation support\nTechnical package\nConsultant coordination",
        "order": 2,
    },
    {
        "title": "Workplace",
        "slug": "workplace",
        "summary": "Workplace projects where frontage, efficiency, envelope performance, and spatial legibility need to work together.",
        "description": "",
        "who_for": "Commercial clients and development teams delivering office buildings, service buildings, or mixed-use workplace environments.",
        "value_proposition": "A design process that keeps the building useful, robust, and recognisable without forcing an unnecessary brand layer onto the architecture.",
        "deliverables": "Feasibility and frontage studies\nDeveloped design\nEnvelope coordination\nTechnical documentation",
        "order": 3,
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
        "featured": False,
        "order": 9,
    },
    {
        "slug": "coastline-civic-centre",
        "title": "Coastline Civic Centre",
        "short_description": "A public building on an exposed waterfront site, organised around clear circulation, sheltered thresholds, and durable civic presence.",
        "category": "civic",
        "status": "completed",
        "location": "Coastal City",
        "year": 2023,
        "area": "2 150 m²",
        "overview": "Coastline Civic Centre was commissioned as a compact public building serving community events, reading rooms, and neighbourhood services on a prominent coastal site. The project combines a durable outer shell with a calm internal circulation sequence, giving the building a public identity that feels welcoming rather than ceremonial.",
        "challenge": "The site was highly exposed to wind and shifting weather, and the brief combined different public uses that needed to coexist without the building feeling over-programmed. The project also needed to read clearly from a distance in a sparse waterfront setting.",
        "concept": "The building is organised around a sheltered public threshold and a clear internal route that links the main civic rooms. Rather than relying on formal complexity, the project uses proportion, depth, and daylight to make movement through the building intuitive.",
        "outcome": "The completed building functions as a stable civic anchor: visible from the waterfront, easy to enter, and flexible enough to support different kinds of public use across the week.",
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
        "slug": "harbour-court-apartments",
        "title": "Harbour Court Apartments",
        "short_description": "A multi-unit housing project that balances exposed urban-edge conditions with clear circulation, durable materials, and sheltered shared space.",
        "category": "housing",
        "status": "completed",
        "location": "Harbour District",
        "year": 2024,
        "area": "4 200 m²",
        "overview": "Harbour Court Apartments is a housing project on a newly developed urban-edge site close to the waterfront. The brief called for robust apartment buildings with clear access, practical layouts, and a strong street presence without resorting to a singular formal gesture.",
        "challenge": "The exposed site required a durable envelope and carefully considered entrances, while the housing layouts needed to feel generous despite tight efficiency targets. The project also had to contribute positively to a district still taking shape.",
        "concept": "The design is based on a simple, legible building form with repeated housing bays, deep openings, and sheltered shared edges. Material decisions were kept restrained so the building could feel settled within a changing urban context.",
        "outcome": "The completed apartments provide efficient housing within a calm and durable shell. The building has helped establish a stronger residential edge to the district while maintaining a clear, understated architectural language.",
        "featured": True,
        "order": 3,
    },
    {
        "slug": "ridgeline-housing",
        "title": "Ridgeline Housing",
        "short_description": "Medium-density housing on an exposed hillside — four blocks stepping with the topography, oriented to maximise solar gain while managing weather exposure and communal access.",
        "category": "housing",
        "status": "completed",
        "location": "Hillside District",
        "year": 2023,
        "area": "1 650 m²",
        "overview": (
            "Four housing blocks arranged along a ridge were commissioned by a housing "
            "association seeking a robust, low-maintenance solution for a difficult site. "
            "The topography — a long south-facing slope with significant wind exposure — "
            "defined both the opportunity and the constraint."
        ),
        "challenge": (
            "The site's orientation offered good solar access but also severe weather "
            "exposure. The challenge was to create housing that felt sheltered and domestic "
            "while meeting the passive solar and ventilation requirements of the brief."
        ),
        "concept": (
            "Each block steps down the slope in section, creating a roofscape that breaks "
            "wind at the communal path level while allowing maximum solar penetration to "
            "south-facing living rooms. Shared access is organised along the upper contour, "
            "keeping vehicles and pedestrians clearly separated."
        ),
        "outcome": (
            "The development was delivered within programme and has performed well in "
            "post-occupancy monitoring. Residents report that the solar design makes the "
            "flats feel significantly warmer than comparable housing in the area, reducing "
            "heating demand noticeably in the first winter of occupancy."
        ),
        "featured": True,
        "order": 4,
    },
    {
        "slug": "harbour-glass-offices",
        "title": "Harbour Glass Offices",
        "short_description": "A contemporary workplace building designed around clear frontage, efficient floorplates, and a restrained commercial identity.",
        "category": "workplace",
        "status": "completed",
        "location": "Harbour District",
        "year": 2022,
        "area": "2 800 m²",
        "overview": "Harbour Glass Offices is a mid-scale workplace project in a new commercial quarter close to the harbour. The brief called for a building that could project a clear professional identity while remaining efficient, adaptable, and durable in an exposed setting.",
        "challenge": "The client needed a building with commercial presence but not excessive branding. The facade had to carry the project's identity while supporting practical floorplates, daylight access, and straightforward servicing.",
        "concept": "The project uses a simple glazed volume with a disciplined structural rhythm and a clear ground-level threshold. Rather than relying on elaborate formal moves, the design focuses on proportion, transparency, and the relationship between the building and the street.",
        "outcome": "The resulting building feels precise and commercially legible without becoming generic. Its strongest quality is the clarity with which structure, frontage, and use align.",
        "featured": True,
        "order": 5,
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
        "order": 7,
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
        "featured": False,
        "order": 10,
    },
    {
        "slug": "civic-waterfront-square",
        "title": "Civic Waterfront Square",
        "short_description": "A reclaimed post-industrial waterfront remade as a public square — hard-landscaped, weather-ready, and designed to be used year-round by the full range of the city's population.",
        "category": "civic",
        "status": "completed",
        "location": "Harbour District",
        "year": 2022,
        "area": "3 200 m²",
        "overview": (
            "A redundant cargo terminal apron was handed back to the city for public use. "
            "The brief was open: create a square that would work for daily life, not just "
            "events — somewhere residents would actually cross, sit in, and return to."
        ),
        "challenge": (
            "Post-industrial waterfronts often become windswept trophy spaces — impressive in "
            "photographs and empty in practice. The challenge was to design a public realm that "
            "acknowledged the scale and exposure of the site while creating sheltered pockets "
            "of use that would function in all seasons."
        ),
        "concept": (
            "The square is organised around a series of low stone walls that run parallel to "
            "the water's edge — defining seating zones, breaking the wind, and providing "
            "informal edges for gathering. A single covered canopy at the inland end marks the "
            "entrance from the city and provides weather protection for the market stalls and "
            "events programme."
        ),
        "outcome": (
            "Within the first summer, the square was used continuously from morning to late "
            "evening. The low walls have become informal seating, skateboard features, and "
            "lunchtime berths in equal measure. The covered canopy hosts a weekly market "
            "and has been adopted for informal performances."
        ),
        "featured": True,
        "order": 6,
    },
    {
        "slug": "housing-block-north-quarter",
        "title": "Housing Block, North Quarter",
        "short_description": "A mid-rise housing block on a tight urban infill site — compact flats arranged around a shared courtyard, with robust envelope design and clear wayfinding throughout.",
        "category": "housing",
        "status": "completed",
        "location": "North Quarter",
        "year": 2024,
        "area": "2 100 m²",
        "overview": (
            "A corner site in a dense residential neighbourhood was redeveloped as a "
            "thirty-flat housing block for a housing association. The brief required a "
            "mix of one- and two-bedroom flats, shared amenity space, and robust "
            "materials suited to a high-traffic urban context."
        ),
        "challenge": (
            "The site geometry — a shallow corner plot with a significant level change — "
            "made it difficult to achieve good daylighting across all units while meeting "
            "the density required by the brief. The design had to resolve both the "
            "planning massing constraints and the internal organisation simultaneously."
        ),
        "concept": (
            "The block steps down with the site, creating a roofscape that reduces "
            "bulk in key views while allowing south-facing terraces for upper-floor units. "
            "A shared courtyard at ground level is accessed from two points on the street "
            "grid, giving the block legible thresholds without requiring a staffed entrance."
        ),
        "outcome": (
            "The block achieved planning consent on first submission and was delivered "
            "within programme. Post-occupancy feedback from the housing association noted "
            "that residents valued the courtyard as a key amenity — particularly families "
            "with children and older residents."
        ),
        "featured": True,
        "order": 7,
    },
    {
        "slug": "school-extension-timber-frame",
        "title": "School Extension, Timber Frame",
        "short_description": "A single-storey timber-frame extension to a primary school — adding four classrooms, a shared learning corridor, and direct access to the school garden.",
        "category": "civic",
        "status": "completed",
        "location": "Suburban District",
        "year": 2021,
        "area": "420 m²",
        "overview": (
            "A primary school with insufficient classroom capacity required a permanent "
            "extension to replace long-standing temporary buildings. The brief asked for "
            "four new classrooms, improved circulation between the existing school and "
            "the extension, and better access to the school's outdoor spaces."
        ),
        "challenge": (
            "The site was constrained on three sides by the existing school building, "
            "outdoor play areas, and a protected tree line. The extension had to fit "
            "within these constraints while maintaining fire separation from the main "
            "building and meeting current educational space standards."
        ),
        "concept": (
            "A single-storey pavilion organised as a shared learning corridor with "
            "classrooms on the south side and a continuous covered outdoor teaching "
            "terrace linking to the garden. The timber structure is left exposed internally, "
            "providing a warm, legible ceiling that contributes to the acoustic performance "
            "of the rooms."
        ),
        "outcome": (
            "The extension opened ahead of the autumn term and was adopted immediately "
            "as the school's preferred teaching space. The outdoor terrace is used daily "
            "for science lessons and informal outdoor learning in all but the coldest weather."
        ),
        "featured": False,
        "order": 8,
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
        else:
            # Auto-discover bundled demo media when --media-dir is not given
            from django.conf import settings
            _candidate = _discover_demo_media_dir(settings.MEDIA_ROOT)
            if _candidate:
                media_dir = _candidate
                self.stdout.write(f"Auto-discovered demo media: {media_dir}")

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
            obj, created = Service.objects.get_or_create(
                slug=data["slug"],
                defaults={"title": data["title"]},
            )
            for key, value in data.items():
                if key != "slug":
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
        attached = 0
        warnings = 0

        for slug, relative_source in DEMO_COVER_SOURCES.items():
            cover_file = media_dir / relative_source
            if not cover_file.is_file():
                warnings += self._warn(f"cover source not found for '{slug}': {cover_file}")
                continue
            try:
                project = Project.objects.get(slug=slug)
            except Project.DoesNotExist:
                warnings += self._warn(f"Project with slug '{slug}' not found — skipping cover")
                continue

            # Skip if same file already attached
            if project.cover_image and _stem_clean(project.cover_image.name) == slug:
                self.stdout.write(f"  SKIP cover for '{slug}' (already attached): {cover_file.name}")
                attached += 1
                continue

            destination_name = f"{slug}{cover_file.suffix.lower()}"
            with cover_file.open("rb") as fh:
                project.cover_image.save(destination_name, File(fh), save=True)
            self.stdout.write(f"  Attached cover for '{slug}' → {project.cover_image.name}")
            attached += 1

        return attached, warnings

    def _attach_galleries(self, media_dir: Path) -> tuple[int, int]:
        """Attach gallery images for the projects that should have them.
        Returns (count_new_images_added, warning_count)."""
        total_added = 0
        warnings = 0

        for slug, relative_sources in DEMO_GALLERY_SOURCES.items():
            try:
                project = Project.objects.get(slug=slug)
            except Project.DoesNotExist:
                warnings += self._warn(f"Project with slug '{slug}' not found — skipping gallery")
                continue

            image_files = [media_dir / rel for rel in relative_sources]
            missing = [path for path in image_files if not path.is_file()]
            if missing:
                warnings += self._warn(f"gallery source missing for '{slug}': {missing[0]}")
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
