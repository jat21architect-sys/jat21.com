"""
View tests for apps.pages: home and about pages.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.projects.models import Project, ProjectImage
from apps.site.about_defaults import (
    PRACTICE_STRUCTURE_PROMPT,
    PROFESSIONAL_STANDING_PROMPT,
    PROJECT_LEADERSHIP_PROMPT,
)
from apps.site.models import AboutProfile, SiteSettings


@pytest.mark.django_db
def test_home_page(client, site_settings):
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert b"Test Site" in response.content  # hero h1 renders site_name
    assert b"/static/images/og-default.svg" in response.content


@pytest.mark.django_db
def test_homepage_hero_and_featured_cards_emit_image_dimensions_and_priority(
    client, site_settings, make_uploaded_image
):
    hero_project = Project.objects.create(
        title="Hero Project",
        slug="hero-project",
        short_description="Hero project.",
        category="housing",
        status="completed",
        featured=True,
        order=1,
        cover_image=make_uploaded_image("hero.jpg", size=(1600, 900)),
    )
    card_project = Project.objects.create(
        title="Card Project",
        slug="card-project",
        short_description="Card project.",
        category="civic",
        status="completed",
        featured=True,
        order=2,
    )
    gallery_image = ProjectImage.objects.create(
        project=card_project,
        image=make_uploaded_image("card.jpg", size=(1200, 800)),
        alt_text="Card preview",
        order=1,
        image_type="gallery",
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert hero_project.cover_image.url.encode() in response.content
    assert b'fetchpriority="high"' in response.content
    assert b'width="1600"' in response.content
    assert b'height="900"' in response.content
    assert gallery_image.image.url.encode() in response.content
    assert b'decoding="async"' in response.content
    assert b'width="1200"' in response.content
    assert b'height="800"' in response.content


@pytest.mark.django_db
def test_home_page_title_uses_template_neutral_practice_language(client, site_settings):
    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert b"<title>Test Site \xe2\x80\x94 Architecture Practice</title>" in response.content


@pytest.mark.django_db
def test_about_page(client, site_settings):
    response = client.get(reverse("pages:about"))
    assert response.status_code == 200
    assert b'<meta name="description" content="">' in response.content


def _populate_minimum_about(site_settings, **overrides):
    site_settings.location = overrides.pop("site_location", "Reykjavik, Iceland")
    site_settings.contact_email = overrides.pop("site_email", "studio@example.com")
    site_settings.save()

    profile = AboutProfile.load()
    defaults = {
        "identity_mode": AboutProfile.IdentityMode.STUDIO,
        "practice_structure": "Small studio",
        "one_line_practice_description": "Architecture for housing, civic, and workplace projects.",
        "practice_summary": "A practice working across public and private projects.",
        "project_leadership": "Projects are led directly with specialist consultants brought in as needed.",
        "professional_standing": "Registered architectural practice",
        "education": "Master of Architecture",
        "supporting_facts": "",
        "experience_years": 12,
        "approach": "The work prioritises clarity, durability, and legible project decision-making.",
        "closing_invitation": "Get in touch to discuss a housing, civic, or workplace project.",
        "portrait_mode": AboutProfile.PortraitMode.TEXT_ONLY,
    }
    defaults.update(overrides)
    for field, value in defaults.items():
        setattr(profile, field, value)
    profile.save()
    return profile


@pytest.mark.django_db
def test_about_page_uses_person_led_identity_fields(client, site_settings):
    _populate_minimum_about(
        site_settings,
        identity_mode=AboutProfile.IdentityMode.PERSON,
        principal_name="Avery Strand",
        principal_title="Founder and Registered Architect",
    )

    response = client.get(reverse("pages:about"))

    assert response.status_code == 200
    assert b"Avery Strand" in response.content
    assert b"Founder and Registered Architect, Test Site" in response.content


@pytest.mark.django_db
def test_about_page_hides_portrait_block_in_text_only_mode(client, site_settings):
    _populate_minimum_about(site_settings)

    response = client.get(reverse("pages:about"))

    assert response.status_code == 200
    assert b"about-layout--text-only" in response.content
    assert b"about-portrait" not in response.content
    assert b"about-portrait__placeholder" not in response.content


@pytest.mark.django_db
def test_about_page_hides_professional_profile_without_minimum_fact_set(client, site_settings):
    _populate_minimum_about(
        site_settings,
        education="",
        supporting_facts="",
    )

    response = client.get(reverse("pages:about"))

    assert response.status_code == 200
    assert b"Professional Profile" not in response.content


@pytest.mark.django_db
def test_about_page_hides_starter_prompt_fields_from_public_render(client, site_settings):
    _populate_minimum_about(
        site_settings,
        practice_structure=PRACTICE_STRUCTURE_PROMPT,
        project_leadership=PROJECT_LEADERSHIP_PROMPT,
        professional_standing=PROFESSIONAL_STANDING_PROMPT,
        education="[Add education details, one per line]",
        supporting_facts="Registered architectural practice\nPlanning, technical design, and consultant coordination",
    )

    response = client.get(reverse("pages:about"))

    assert response.status_code == 200
    assert PRACTICE_STRUCTURE_PROMPT.encode() not in response.content
    assert PROJECT_LEADERSHIP_PROMPT.encode() not in response.content
    assert PROFESSIONAL_STANDING_PROMPT.encode() not in response.content
    assert b"[Add education details, one per line]" not in response.content
    assert b"Professional Profile" not in response.content


@pytest.mark.django_db
def test_about_page_shows_professional_profile_with_minimum_fact_set(client, site_settings):
    _populate_minimum_about(
        site_settings,
        supporting_facts="Housing and civic project experience",
    )

    response = client.get(reverse("pages:about"))

    assert response.status_code == 200
    assert b"Professional Profile" in response.content
    assert b"Based in Reykjavik, Iceland" in response.content
    assert b"Registered architectural practice" in response.content
    assert b"12+ years in practice" in response.content
    assert b"Housing and civic project experience" in response.content


@pytest.mark.django_db
def test_privacy_page(client, site_settings):
    site_settings.contact_email = "privacy@example.com"
    site_settings.save()
    response = client.get(reverse("pages:privacy"))
    assert response.status_code == 200
    assert b"Privacy" in response.content
    assert b"Privacy contact" in response.content
    assert b"privacy@example.com" in response.content


@pytest.mark.django_db
def test_about_page_falls_back_to_site_meta_description_when_page_meta_blank(client, site_settings):
    site_settings.meta_description = "Default site description."
    site_settings.save()

    response = client.get(reverse("pages:about"))

    assert response.status_code == 200
    assert b'Default site description.' in response.content


@pytest.mark.django_db
def test_homepage_closing_coda_uses_compact_invitation_language(client, site_settings):
    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert b"Bring a site, a brief in progress, or an early question." in response.content
    assert b"Who We Work With" not in response.content
    assert b"Project Types" not in response.content
    assert b"How Work Starts" not in response.content


@pytest.mark.django_db
def test_homepage_shows_featured_projects_only_when_any_featured_exist(client, site_settings):
    """When featured projects exist, homepage shows only featured — never non-featured."""
    featured_a = Project.objects.create(
        title="Featured A", slug="featured-a", short_description=".",
        category="housing", status="completed", featured=True, order=1,
    )
    featured_b = Project.objects.create(
        title="Featured B", slug="featured-b", short_description=".",
        category="civic", status="completed", featured=True, order=2,
    )
    non_featured = Project.objects.create(
        title="Non-Featured", slug="non-featured", short_description=".",
        category="workplace", status="completed", featured=False, order=3,
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    slugs = [p.slug for p in response.context["homepage_projects"]]
    assert featured_a.slug in slugs
    assert featured_b.slug in slugs
    assert non_featured.slug not in slugs


@pytest.mark.django_db
def test_homepage_caps_featured_projects_at_six(client, site_settings):
    """Homepage shows at most 6 featured projects regardless of how many are marked featured."""
    for i in range(8):
        Project.objects.create(
            title=f"Featured {i}", slug=f"featured-{i}", short_description=".",
            category="housing", status="completed", featured=True, order=i,
        )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert len(response.context["homepage_projects"]) == 6
    assert response.context["homepage_projects_count"] == 6


@pytest.mark.django_db
def test_homepage_falls_back_to_recent_projects_when_none_are_featured(client, site_settings):
    """When no projects are marked featured, homepage falls back to recent published projects."""
    recent = Project.objects.create(
        title="Recent Project", slug="recent-project", short_description=".",
        category="housing", status="completed", featured=False, order=1,
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    slugs = [p.slug for p in response.context["homepage_projects"]]
    assert recent.slug in slugs


@pytest.mark.django_db
def test_homepage_context_exposes_hero_project(client, site_settings):
    first = Project.objects.create(
        title="First Selected",
        slug="first-selected",
        short_description="First project.",
        category="housing",
        status="completed",
        featured=True,
        order=1,
    )
    Project.objects.create(
        title="Second Selected",
        slug="second-selected",
        short_description="Second project.",
        category="civic",
        status="completed",
        featured=True,
        order=2,
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert response.context["hero_project"] == first


@pytest.mark.django_db
def test_home_project_cards_fall_back_to_first_gallery_image(client, site_settings):
    featured = Project.objects.create(
        title="Hero Project",
        slug="hero-project",
        short_description="Lead project.",
        category="workplace",
        status="completed",
        featured=True,
        cover_image=SimpleUploadedFile("hero.jpg", b"hero-image", content_type="image/jpeg"),
    )
    fallback_project = Project.objects.create(
        title="Gallery Preview Project",
        slug="gallery-preview-project",
        short_description="Uses a gallery image on cards.",
        category="housing",
        status="completed",
        featured=True,
    )
    gallery_image = ProjectImage.objects.create(
        project=fallback_project,
        image=SimpleUploadedFile("preview.jpg", b"preview-image", content_type="image/jpeg"),
        alt_text="Preview facade",
        order=1,
        image_type="gallery",
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert featured.cover_image.url.encode() in response.content
    assert gallery_image.image.url.encode() in response.content
    assert b"project-card__placeholder" not in response.content


@pytest.mark.django_db
def test_homepage_uses_featured_projects_strip_and_updated_cta(client, site_settings):
    Project.objects.create(
        title="Selected Project",
        slug="selected-project",
        short_description="Homepage project.",
        category="workplace",
        status="completed",
        featured=True,
        order=1,
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert b"Featured Projects" in response.content
    assert b"View All" in response.content
    assert b"All Projects" not in response.content
    assert b"Housing, civic, and workplace projects from the studio" not in response.content
    assert b"More Work" not in response.content
    assert b"Design Services" not in response.content
    assert b"Client testimonials" not in response.content
    assert b"homepage-coda" in response.content
    assert b"Get in Touch" in response.content


@pytest.mark.django_db
def test_footer_includes_privacy_link(client, site_settings):
    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert reverse("pages:privacy").encode() in response.content
    assert b"Privacy" in response.content


# ---------------------------------------------------------------------------
# Homepage — admin-editable per-breakpoint project counts
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_homepage_context_exposes_hp_counts(client, site_settings):
    """View must expose hp_mobile, hp_tablet, hp_desktop context variables."""
    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert "hp_mobile" in response.context
    assert "hp_tablet" in response.context
    assert "hp_desktop" in response.context
    # Defaults from SiteSettings model
    assert response.context["hp_mobile"] == 3
    assert response.context["hp_tablet"] == 4
    assert response.context["hp_desktop"] == 6


@pytest.mark.django_db
def test_homepage_query_respects_desktop_count(client, site_settings):
    """When desktop count is set to 4, only 4 featured projects are returned."""
    site_settings.homepage_projects_desktop_count = 4
    site_settings.save()

    for i in range(6):
        Project.objects.create(
            title=f"Featured {i}", slug=f"feat-dc-{i}", short_description=".",
            category="housing", status="completed", featured=True, order=i,
        )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert len(response.context["homepage_projects"]) == 4


@pytest.mark.django_db
def test_homepage_grid_has_breakpoint_count_classes(client, site_settings):
    """Grid container must carry hp-mob-N and hp-tab-N classes matching SiteSettings values."""
    site_settings.homepage_projects_mobile_count = 2
    site_settings.homepage_projects_tablet_count = 3
    site_settings.homepage_projects_desktop_count = 6
    site_settings.save()

    Project.objects.create(
        title="Grid Class Project", slug="grid-class-proj", short_description=".",
        category="housing", status="completed", featured=True, order=1,
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert b"hp-mob-2" in response.content
    assert b"hp-tab-3" in response.content


# ---------------------------------------------------------------------------
# Hero label and compact mode
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_hero_label_absent_when_blank(client, site_settings):
    """When hero_label is blank the label element must not appear in the DOM."""
    site_settings.hero_label = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert b"hero__label" not in response.content


@pytest.mark.django_db
def test_hero_label_rendered_when_set(client, site_settings):
    """When hero_label is set it must appear in the hero section."""
    site_settings.hero_label = "Architecture & Urbanism"
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert b"Architecture &amp; Urbanism" in response.content
    assert b"hero__label" in response.content


@pytest.mark.django_db
def test_hero_tagline_absent_when_blank(client, site_settings):
    """When tagline is blank the subtitle element must not appear in the DOM."""
    site_settings.tagline = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert b"hero__subtitle" not in response.content


@pytest.mark.django_db
def test_hero_compact_class_absent_by_default(client, site_settings):
    """hero--compact modifier must not be present when hero_compact is False."""
    assert site_settings.hero_compact is False
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert b"hero--compact" not in response.content


@pytest.mark.django_db
def test_hero_compact_class_present_when_enabled(client, site_settings):
    """hero--compact modifier must appear on the section element when hero_compact is True."""
    site_settings.hero_compact = True
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert b"hero--compact" in response.content


@pytest.mark.django_db
def test_homepage_hero_renders_selected_cover_image_as_eager_background(
    client, site_settings, make_uploaded_image
):
    featured = Project.objects.create(
        title="Hero Cover Project",
        slug="hero-cover-project",
        short_description="Hero image project.",
        category="housing",
        status="completed",
        featured=True,
        order=1,
        cover_image=make_uploaded_image("hero-cover.jpg", size=(1600, 900)),
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert featured.cover_image.url.encode() in response.content
    assert b'class="hero__bg"' in response.content
    assert b'loading="eager"' in response.content
    assert b'fetchpriority="high"' in response.content
    assert b'width="1600"' in response.content
    assert b'height="900"' in response.content


@pytest.mark.django_db
def test_site_settings_hero_fields_default(db):
    """hero_label defaults blank and hero_compact defaults False."""
    s = SiteSettings.load()
    assert s.hero_label == ""
    assert s.hero_compact is False


# ---------------------------------------------------------------------------
# Navbar brand — nav_name fallback logic
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_nav_renders_site_name_when_nav_name_blank(client, site_settings):
    """When nav_name is blank and no logo, site_name appears in nav brand."""
    site_settings.site_name = "Test Studio"
    site_settings.nav_name = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b"Test Studio" in response.content


@pytest.mark.django_db
def test_nav_renders_nav_name_when_set(client, site_settings):
    """nav_name is rendered in the brand span when set (no logo); site_name still appears in title/hero."""
    site_settings.site_name = "Beaumont Whitfield Kellerman Partnership"
    site_settings.nav_name = "BWK Partnership"
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b"BWK Partnership" in response.content
    # nav_name replaces site_name inside the nav__brand span; site_name still
    # appears in <title>, hero h1, and footer — so we check the nav span directly.
    assert b'class="nav__name">BWK Partnership</span>' in response.content
    assert b'class="nav__name">Beaumont Whitfield Kellerman Partnership</span>' not in response.content


@pytest.mark.django_db
def test_nav_name_absent_renders_site_name(client, site_settings):
    """Regression: when nav_name is blank, site_name is used (not an empty span)."""
    site_settings.site_name = "Strand Architecture"
    site_settings.nav_name = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b"Strand Architecture" in response.content


# ---------------------------------------------------------------------------
# Navbar brand — monogram fallback (spec v3)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_nav_renders_full_text_when_site_name_fits(client, site_settings):
    """site_name ≤ 18 chars and ≤ 2 words → full text in nav__name span."""
    site_settings.site_name = "Atelier Nord"   # 12 chars, 2 words
    site_settings.nav_name = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b'class="nav__name">Atelier Nord</span>' in response.content
    assert b"nav__monogram" not in response.content


@pytest.mark.django_db
def test_nav_renders_monogram_when_site_name_too_long(client, site_settings):
    """site_name > 18 chars, no logo, no nav_name → monogram span rendered."""
    site_settings.site_name = "Beaumont Whitfield Kellerman Partnership"
    site_settings.nav_name = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b'class="nav__monogram">BWK</span>' in response.content
    assert b'class="nav__name">Beaumont Whitfield' not in response.content


@pytest.mark.django_db
def test_nav_monogram_has_aria_label(client, site_settings):
    """Brand anchor always carries aria-label with full site_name."""
    site_settings.site_name = "Beaumont Whitfield Kellerman Partnership"
    site_settings.nav_name = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b'aria-label="Beaumont Whitfield Kellerman Partnership"' in response.content


@pytest.mark.django_db
def test_nav_nav_name_suppresses_monogram(client, site_settings):
    """nav_name set → nav_name text rendered; monogram path not entered."""
    site_settings.site_name = "Beaumont Whitfield Kellerman Partnership"
    site_settings.nav_name = "BWK Partnership"
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b'class="nav__name">BWK Partnership</span>' in response.content
    assert b"nav__monogram" not in response.content


@pytest.mark.django_db
def test_nav_monogram_triggered_by_word_count(client, site_settings):
    """3-word name triggers monogram even when char count would fit."""
    site_settings.site_name = "Studio of Form"   # 14 chars, 3 words
    site_settings.nav_name = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b"nav__monogram" in response.content
    assert b'class="nav__name">Studio of Form</span>' not in response.content


@pytest.mark.django_db
def test_nav_full_text_has_aria_label(client, site_settings):
    """aria-label is present even when rendering the full short name as text."""
    site_settings.site_name = "Atelier Nord"
    site_settings.nav_name = ""
    site_settings.save()
    response = client.get(reverse("pages:home"))
    assert b'aria-label="Atelier Nord"' in response.content


@pytest.mark.parametrize(
    ("route_name", "expected_fragment"),
    [
        ("projects:list", b'class="nav__link is-active" aria-current="page">Projects</a>'),
        ("pages:about", b'class="nav__link is-active" aria-current="page">About</a>'),
        ("services:list", b'class="nav__link is-active" aria-current="page">Services</a>'),
        ("contact:contact", b'class="nav__link nav__cta is-active" aria-current="page">Contact</a>'),
    ],
)
@pytest.mark.django_db
def test_nav_marks_current_route_active(client, site_settings, route_name, expected_fragment):
    response = client.get(reverse(route_name))

    assert response.status_code == 200
    assert expected_fragment in response.content
