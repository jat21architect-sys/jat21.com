"""
View tests for apps.pages: home and about pages.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.core.about_defaults import (
    PRACTICE_STRUCTURE_PROMPT,
    PROFESSIONAL_STANDING_PROMPT,
    PROJECT_LEADERSHIP_PROMPT,
)
from apps.core.models import AboutProfile
from apps.projects.models import Project, ProjectImage


@pytest.mark.django_db
def test_home_page(client, site_settings):
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    assert b"Architecture Practice" in response.content
    assert b"/static/images/og-default.svg" in response.content


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
def test_homepage_projects_merge_featured_and_supporting_work(client, site_settings):
    """Homepage projects should show featured work first, then fill from supporting work."""
    featured_one = Project.objects.create(
        title="Featured One",
        slug="featured-one",
        short_description="Featured project.",
        category="workplace",
        status="completed",
        featured=True,
        order=2,
    )
    featured_two = Project.objects.create(
        title="Featured Two",
        slug="featured-two",
        short_description="Featured project.",
        category="civic",
        status="completed",
        featured=True,
        order=1,
    )
    supporting_one = Project.objects.create(
        title="Supporting One",
        slug="supporting-one",
        short_description="Supporting project.",
        category="housing",
        status="completed",
        featured=False,
        order=3,
    )
    supporting_two = Project.objects.create(
        title="Supporting Two",
        slug="supporting-two",
        short_description="Supporting project.",
        category="housing",
        status="completed",
        featured=False,
        order=4,
    )
    supporting_three = Project.objects.create(
        title="Supporting Three",
        slug="supporting-three",
        short_description="Supporting project.",
        category="housing",
        status="completed",
        featured=False,
        order=5,
    )

    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    project_slugs = [p.slug for p in response.context["homepage_projects"]]
    assert project_slugs == [
        featured_two.slug,
        featured_one.slug,
        supporting_one.slug,
        supporting_two.slug,
    ]
    assert supporting_three.slug not in project_slugs


@pytest.mark.django_db
def test_homepage_context_exposes_last_selected_project_for_coda(client, site_settings):
    first = Project.objects.create(
        title="First Selected",
        slug="first-selected",
        short_description="First project.",
        category="housing",
        status="completed",
        featured=True,
        order=1,
    )
    second = Project.objects.create(
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
    assert response.context["home_coda_project"] == second
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
def test_homepage_uses_selected_projects_strip_and_updated_cta(client, site_settings):
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
    assert b"Selected Projects" in response.content
    assert b"Housing, civic, and workplace projects from the studio" not in response.content
    assert b"More Work" not in response.content
    assert b"Design Services" not in response.content
    assert b"Client testimonials" not in response.content
    assert b"Start Here" in response.content
    assert b"Get in Touch" in response.content


@pytest.mark.django_db
def test_footer_includes_privacy_link(client, site_settings):
    response = client.get(reverse("pages:home"))

    assert response.status_code == 200
    assert reverse("pages:privacy").encode() in response.content
    assert b"Privacy" in response.content
