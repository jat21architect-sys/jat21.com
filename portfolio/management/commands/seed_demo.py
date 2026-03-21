"""
Management command: python manage.py seed_demo

Creates initial demo content — SiteSettings, AboutProfile, Services, and
three placeholder projects — so the site renders immediately after setup.
Run once; safe to re-run (uses get_or_create).
"""

from django.core.management.base import BaseCommand

from portfolio.models import AboutProfile, SiteSettings
from projects.models import Project, Testimonial
from services.models import Service

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
        "title": "House on the Hillside",
        "short_description": "A private residence that uses the natural topography of its sloping site to create a sequence of connected levels, each framing a distinct view of the landscape.",
        "category": "residential",
        "status": "completed",
        "location": "Eastern Cape",
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
        "title": "Community Library Pavilion",
        "short_description": "A lightweight civic pavilion housing a branch library, reading rooms, and flexible community space — designed to be both a landmark and a welcoming public threshold.",
        "category": "cultural",
        "status": "completed",
        "location": "Western Cape",
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
        "title": "Urban Apartment Retrofit",
        "short_description": "The interior transformation of a 1970s apartment block unit — stripping back decades of poor alterations to reveal strong bones and reorganise the plan for contemporary urban living.",
        "category": "interior",
        "status": "completed",
        "location": "Cape Town",
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
        "title": "Commercial Office Conversion",
        "short_description": "The transformation of a decommissioned warehouse into a flexible co-working campus — preserving industrial character while introducing contemporary amenity and environmental performance.",
        "category": "commercial",
        "status": "completed",
        "location": "Johannesburg",
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
        "name": "Sarah & Mark Lindström",
        "role": "Private Clients",
        "company": "",
        "quote": (
            "Working with Jeannot was the best decision we made on this project. "
            "He listened carefully from the very first meeting, never tried to impose "
            "a signature style, and kept us informed at every stage. The house exceeded "
            "what we thought was possible on our budget and timeline."
        ),
        "project_title": "House on the Hillside",
        "order": 1,
    },
    {
        "name": "Nkosi Dlamini",
        "role": "Municipal Library Director",
        "company": "Western Cape District Municipality",
        "quote": (
            "The pavilion has transformed how the community uses the library. We were "
            "worried a striking building might feel intimidating — the opposite happened. "
            "The quality of the space seems to put people at ease. Usage numbers in the "
            "first year were double our projections."
        ),
        "project_title": "Community Library Pavilion",
        "order": 2,
    },
    {
        "name": "Thabo Molefe",
        "role": "Director of Acquisitions",
        "company": "Urban Property Group",
        "quote": (
            "Jeannot delivered a technically complex project on time and within budget, "
            "which alone would make him stand out. But the commercial outcome — full "
            "occupancy inside fourteen months — reflects design quality as much as market "
            "conditions. We will work with him again."
        ),
        "project_title": "Commercial Office Conversion",
        "order": 3,
    },
]


class Command(BaseCommand):
    help = (
        "Seed demo/placeholder content: SiteSettings, AboutProfile, Services, and example "
        "Projects with fictional testimonials (names are placeholders — replace via admin "
        "before launch). Safe to re-run; existing records are updated, not duplicated."
    )

    def handle(self, *args, **options):
        self._seed_settings()
        self._seed_about()
        self._seed_services()
        self._seed_projects()
        self._seed_testimonials()
        self.stdout.write(self.style.SUCCESS("Demo content seeded successfully."))

    def _seed_settings(self):
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        settings.site_name = "Jeannot Tsirenge"
        settings.tagline = "Architectural design shaped by context, clarity, and identity."
        settings.contact_email = "contact@jeannot-tsirenge.com"
        settings.location = "South Africa"
        settings.meta_description = (
            "Jeannot Tsirenge is an architect whose work combines spatial clarity, "
            "contextual sensitivity, and thoughtful design to create places with identity, "
            "purpose, and lasting value."
        )
        settings.save()
        action = "Created" if created else "Updated"
        self.stdout.write(f"  {action} SiteSettings")

    def _seed_about(self):
        profile, created = AboutProfile.objects.get_or_create(pk=1)
        profile.headline = "An architect whose work is shaped by context, clarity, and care."
        profile.intro = (
            "Jeannot Tsirenge is an architect whose work combines spatial clarity, "
            "contextual sensitivity, and thoughtful design to create places with identity, "
            "purpose, and lasting value."
        )
        profile.biography = (
            "Jeannot Tsirenge is a registered architect with a practice spanning residential, "
            "cultural, and commercial projects across sub-Saharan Africa. His work is characterised "
            "by a commitment to design quality, material honesty, and a genuine engagement with "
            "the specific conditions of each site and brief.\n\n"
            "After completing his studies in architecture, he worked with several award-winning "
            "practices before establishing his own independent practice. His work has been recognised "
            "in a number of regional competitions and has been exhibited at professional venues."
        )
        profile.philosophy = (
            "Architecture is not primarily about buildings. It is about the relationship between "
            "people and space — the way a room makes you feel when you enter it, the quality of "
            "light on a surface at a particular time of day, the sequence through which a building "
            "reveals itself. These are the things that make architecture matter.\n\n"
            "I believe in design that is specific — to its place, its programme, and the people "
            "who will use it. This specificity is what distinguishes a good building from a generic one, "
            "and what gives architecture its capacity to create genuine value in the world."
        )
        profile.credentials = (
            "Bachelor of Architecture (Professional)\n"
            "Registered Architect — South African Council for the Architectural Profession (SACAP)\n"
            "Member — South African Institute of Architects (SAIA)"
        )
        profile.experience_years = 8
        profile.location = "South Africa"
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
            obj, created = Project.objects.get_or_create(title=data["title"])
            for key, value in data.items():
                if key != "title":
                    setattr(obj, key, value)
            obj.save()
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} Project: {obj.title}")

    def _seed_testimonials(self):
        for data in TESTIMONIALS:
            project = None
            project_title = data.pop("project_title", None)
            if project_title:
                project = Project.objects.filter(title=project_title).first()
            obj, created = Testimonial.objects.get_or_create(
                name=data["name"],
                defaults={"project": project},
            )
            for key, value in data.items():
                if key != "name":
                    setattr(obj, key, value)
            obj.project = project
            obj.save()
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} Testimonial: {obj.name}")
