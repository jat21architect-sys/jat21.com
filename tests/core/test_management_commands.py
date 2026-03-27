"""
Tests for check_content_readiness management command.

Tests call collect_warnings() directly to avoid sys.exit() in tests.
Each test runs against a fresh isolated DB (pytest-django default).
"""

import pytest
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.about_defaults import (
    CLOSING_INVITATION_DEFAULT,
    PRACTICE_STRUCTURE_PROMPT,
    PROFESSIONAL_STANDING_PROMPT,
    PROJECT_LEADERSHIP_PROMPT,
)
from apps.core.management.commands.check_content_readiness import (
    collect_readiness_issues,
    collect_warnings,
)
from apps.core.models import AboutProfile, SiteSettings
from apps.projects.models import Project, Testimonial

# ---------------------------------------------------------------------------
# SiteSettings checks
# ---------------------------------------------------------------------------


def _populate_minimum_ready_site_and_about():
    site = SiteSettings.load()
    site.site_name = "Studio Rossi"
    site.contact_email = "studio@mypractice.com"
    site.tagline = "Context-led architecture"
    site.meta_description = "Independent architectural practice."
    site.location = "Reykjavik, Iceland"
    site.og_image = SimpleUploadedFile("og.jpg", b"og-image", content_type="image/jpeg")
    site.save()

    about = AboutProfile.load()
    about.identity_mode = AboutProfile.IdentityMode.STUDIO
    about.practice_structure = "Small studio"
    about.one_line_practice_description = "Architecture for housing, civic, and workplace projects."
    about.practice_summary = "A Reykjavik-based practice working across public and private projects."
    about.project_leadership = (
        "Projects are led directly with specialist consultants involved as needed."
    )
    about.professional_standing = "Registered architectural practice"
    about.education = "Master of Architecture"
    about.supporting_facts = ""
    about.experience_years = 12
    about.approach = "The work focuses on clarity, durability, and legible project decision-making."
    about.closing_invitation = "Get in touch to discuss a project."
    about.portrait_mode = AboutProfile.PortraitMode.TEXT_ONLY
    about.save()
    return site, about


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
    about.practice_structure = "Small studio"
    about.one_line_practice_description = "[Add a one-line public description of the practice]"
    about.save()

    warnings = collect_warnings()
    assert any("starter placeholder markers" in w for w in warnings)


@pytest.mark.django_db
def test_about_readiness_warns_but_does_not_block_in_text_only_mode(service, project):
    _populate_minimum_ready_site_and_about()

    blockers, warnings = collect_readiness_issues()

    assert not any("AboutProfile" in blocker for blocker in blockers)
    assert any("text-only mode" in warning for warning in warnings)


@pytest.mark.django_db
def test_readiness_warns_when_page_specific_meta_descriptions_are_blank(service, project):
    _populate_minimum_ready_site_and_about()

    blockers, warnings = collect_readiness_issues()

    assert not any("meta_description is blank" in blocker for blocker in blockers)
    assert any("about_meta_description is blank" in warning for warning in warnings)
    assert any("services_meta_description is blank" in warning for warning in warnings)
    assert any("projects_meta_description is blank" in warning for warning in warnings)
    assert any("contact_meta_description is blank" in warning for warning in warnings)


@pytest.mark.django_db
def test_readiness_warns_when_custom_og_image_is_missing_but_no_longer_blocks(service, project):
    site, _ = _populate_minimum_ready_site_and_about()
    site.og_image.delete(save=True)

    blockers, warnings = collect_readiness_issues()

    assert not any("SiteSettings.og_image is missing" in blocker for blocker in blockers)
    assert any("SiteSettings.og_image is missing" in warning for warning in warnings)


@pytest.mark.django_db
def test_seed_about_sets_safe_default_invitation_and_truth_prompts():
    about = AboutProfile.load()

    call_command("seed_about")
    about.refresh_from_db()

    assert about.practice_structure == PRACTICE_STRUCTURE_PROMPT
    assert about.project_leadership == PROJECT_LEADERSHIP_PROMPT
    assert about.professional_standing == PROFESSIONAL_STANDING_PROMPT
    assert about.closing_invitation == CLOSING_INVITATION_DEFAULT


@pytest.mark.django_db
def test_about_readiness_warns_when_truth_fields_are_omitted_or_starter_prompts(service, project):
    _, about = _populate_minimum_ready_site_and_about()
    about.practice_structure = PRACTICE_STRUCTURE_PROMPT
    about.project_leadership = ""
    about.professional_standing = PROFESSIONAL_STANDING_PROMPT
    about.save()

    blockers, warnings = collect_readiness_issues()

    assert not any("practice_structure" in blocker for blocker in blockers)
    assert not any("project_leadership" in blocker for blocker in blockers)
    assert not any("professional_standing" in blocker for blocker in blockers)
    assert any("practice_structure is omitted or still a starter prompt" in warning for warning in warnings)
    assert any("project_leadership is omitted or still a starter prompt" in warning for warning in warnings)
    assert any("professional_standing is omitted or still a starter prompt" in warning for warning in warnings)


@pytest.mark.django_db
def test_about_readiness_blocks_when_person_led_name_is_missing(service, project):
    _, about = _populate_minimum_ready_site_and_about()
    about.identity_mode = AboutProfile.IdentityMode.PERSON
    about.principal_title = "Founder and Registered Architect"
    about.save()

    blockers, _ = collect_readiness_issues()

    assert any("principal_name" in blocker for blocker in blockers)


@pytest.mark.django_db
def test_about_readiness_blocks_when_minimum_profile_fact_set_is_missing(service, project):
    _, about = _populate_minimum_ready_site_and_about()
    about.education = ""
    about.supporting_facts = ""
    about.save()

    blockers, _ = collect_readiness_issues()

    assert any("concrete supporting fact" in blocker for blocker in blockers)


@pytest.mark.django_db
def test_about_readiness_blocks_when_optional_proof_fields_contain_only_starter_prompts(service, project):
    _, about = _populate_minimum_ready_site_and_about()
    about.education = "[Add education details, one per line]"
    about.supporting_facts = "[Add at least one concrete supporting fact, one per line]"
    about.save()

    blockers, _ = collect_readiness_issues()

    assert any("concrete supporting fact" in blocker for blocker in blockers)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("field", "value", "expected_message"),
    [
        (
            "practice_structure",
            PRACTICE_STRUCTURE_PROMPT,
            "AboutProfile.practice_structure is omitted or still a starter prompt.",
        ),
        (
            "project_leadership",
            PROJECT_LEADERSHIP_PROMPT,
            "AboutProfile.project_leadership is omitted or still a starter prompt.",
        ),
        (
            "professional_standing",
            PROFESSIONAL_STANDING_PROMPT,
            "AboutProfile.professional_standing is omitted or still a starter prompt.",
        ),
    ],
)
def test_about_readiness_warns_when_truth_fields_are_still_starter_prompts(
    service,
    project,
    field,
    value,
    expected_message,
):
    _, about = _populate_minimum_ready_site_and_about()
    setattr(about, field, value)
    about.closing_invitation = CLOSING_INVITATION_DEFAULT
    about.save()

    blockers, warnings = collect_readiness_issues()

    assert not any(field in blocker for blocker in blockers)
    assert any(expected_message in warning for warning in warnings)
    assert not any("closing_invitation is blank" in blocker for blocker in blockers)


@pytest.mark.django_db
def test_about_readiness_does_not_add_generic_placeholder_blocker_for_optional_proof_prompts(
    service, project
):
    _, about = _populate_minimum_ready_site_and_about()
    about.education = "[Add education details, one per line]"
    about.closing_invitation = CLOSING_INVITATION_DEFAULT
    about.save()

    blockers, _ = collect_readiness_issues()

    assert not any("starter placeholder markers" in blocker for blocker in blockers)


# ---------------------------------------------------------------------------
# Content collection checks
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_warns_when_no_active_services():
    # Fresh DB has no services.
    warnings = collect_warnings()
    assert any("No active Service records found" in w for w in warnings)


@pytest.mark.django_db
def test_no_service_warning_when_active_service_exists(service):
    # `service` fixture (conftest) creates one active Service.
    warnings = collect_warnings()
    assert not any("No active Service records found" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_no_projects():
    # Fresh DB has no projects.
    warnings = collect_warnings()
    assert any("No Project records found" in w for w in warnings)


@pytest.mark.django_db
def test_no_project_warning_when_project_exists(project):
    # `project` fixture (conftest) creates one Project.
    warnings = collect_warnings()
    assert not any("No Project records found" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_demo_projects_exist(site_settings):
    Project.objects.create(
        title="House on the Hillside",
        short_description="Starter project.",
        category="housing",
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
