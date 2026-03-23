"""
Tests for check_content_readiness management command.

Tests call collect_warnings() directly to avoid sys.exit() in tests.
Each test runs against a fresh isolated DB (pytest-django default).
"""

import pytest

from apps.core.management.commands.check_content_readiness import collect_warnings
from apps.core.models import AboutProfile, SiteSettings
from apps.projects.models import Project, Testimonial

# ---------------------------------------------------------------------------
# SiteSettings checks
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_warns_when_site_name_is_blank():
    # SiteSettings.load() on a fresh DB creates with site_name = "" (blank default).
    warnings = collect_warnings()
    assert any("site_name" in w for w in warnings)


@pytest.mark.django_db
def test_no_site_name_warning_when_customised():
    site = SiteSettings.load()
    site.site_name = "Priya Patel Architecture"
    site.save()
    warnings = collect_warnings()
    assert not any("site_name" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_contact_email_is_blank():
    # SiteSettings.load() creates with contact_email = "" (blank default).
    warnings = collect_warnings()
    assert any("contact_email" in w for w in warnings)


@pytest.mark.django_db
def test_no_contact_email_warning_when_customised():
    site = SiteSettings.load()
    site.contact_email = "studio@mypractice.com"
    site.save()
    warnings = collect_warnings()
    assert not any("contact_email" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_site_name_is_still_demo_value():
    site = SiteSettings.load()
    site.site_name = "Demo Architecture Studio"
    site.contact_email = "studio@mypractice.com"
    site.save()
    warnings = collect_warnings()
    assert any("starter value ('Demo Architecture Studio')" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_contact_email_is_still_demo_value():
    site = SiteSettings.load()
    site.site_name = "Studio Rossi"
    site.contact_email = "hello@demo-architecture.example"
    site.save()
    warnings = collect_warnings()
    assert any("hello@demo-architecture.example" in w for w in warnings)


# ---------------------------------------------------------------------------
# AboutProfile checks
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_warns_when_experience_years_is_zero():
    # AboutProfile.load() on a fresh DB has experience_years=0 (model default).
    warnings = collect_warnings()
    assert any("experience_years" in w for w in warnings)


@pytest.mark.django_db
def test_no_experience_years_warning_when_set():
    about = AboutProfile.load()
    about.experience_years = 12
    about.save()
    warnings = collect_warnings()
    assert not any("experience_years" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_about_contains_placeholder_markers():
    site = SiteSettings.load()
    site.site_name = "Studio Rossi"
    site.contact_email = "studio@mypractice.com"
    site.save()

    about = AboutProfile.load()
    about.headline = "About the Practice"
    about.intro = "[Your Name] is an architect working across residential projects."
    about.save()

    warnings = collect_warnings()
    assert any("starter placeholder markers" in w for w in warnings)


# ---------------------------------------------------------------------------
# Content collection checks
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_warns_when_no_active_services():
    # Fresh DB has no services.
    warnings = collect_warnings()
    assert any("Service" in w for w in warnings)


@pytest.mark.django_db
def test_no_service_warning_when_active_service_exists(service):
    # `service` fixture (conftest) creates one active Service.
    warnings = collect_warnings()
    assert not any("Service" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_no_projects():
    # Fresh DB has no projects.
    warnings = collect_warnings()
    assert any("Project" in w for w in warnings)


@pytest.mark.django_db
def test_no_project_warning_when_project_exists(project):
    # `project` fixture (conftest) creates one Project.
    warnings = collect_warnings()
    assert not any("Project" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_demo_projects_exist(site_settings):
    Project.objects.create(
        title="House on the Hillside",
        short_description="Starter project.",
        category="residential",
        status="completed",
    )
    warnings = collect_warnings()
    assert any("Starter Project records are still present" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_demo_testimonials_exist(project):
    Testimonial.objects.create(
        project=project,
        name="Sarah & Mark L.",
        role="Private Clients",
        quote="Starter testimonial.",
    )
    warnings = collect_warnings()
    assert any("Starter Testimonial records are still present" in w for w in warnings)
