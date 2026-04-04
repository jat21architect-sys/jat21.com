"""
Admin unit tests for apps.site: SiteSettings and AboutProfile singleton guards.
"""

import pytest
from django.contrib import admin
from django.contrib.messages import INFO, WARNING
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, override_settings

from apps.services.models import Service
from apps.site.admin.site import AboutProfileAdmin, SiteSettingsAdmin
from apps.site.models import AboutProfile, SiteSettings


@pytest.fixture
def rf():
    return RequestFactory()


def _populate_minimum_ready_site_and_about():
    site = SiteSettings.load()
    site.site_name = "Studio Rossi"
    site.contact_email = "studio@example.com"
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

    Service.objects.create(
        title="Architectural Design",
        slug="architectural-design",
        summary="Full design service.",
        order=1,
        active=True,
    )


@pytest.mark.django_db
def test_site_settings_admin_allows_add_when_empty(rf):
    a = SiteSettingsAdmin(SiteSettings, admin.site)
    assert a.has_add_permission(rf.get("/admin/")) is True


@pytest.mark.django_db
def test_site_settings_admin_blocks_add_when_row_exists(rf):
    SiteSettings.objects.create(pk=1)
    a = SiteSettingsAdmin(SiteSettings, admin.site)
    assert a.has_add_permission(rf.get("/admin/")) is False


@pytest.mark.django_db
def test_about_profile_admin_allows_add_when_empty(rf):
    a = AboutProfileAdmin(AboutProfile, admin.site)
    assert a.has_add_permission(rf.get("/admin/")) is True


@pytest.mark.django_db
def test_about_profile_admin_blocks_add_when_row_exists(rf):
    AboutProfile.objects.create(pk=1)
    a = AboutProfileAdmin(AboutProfile, admin.site)
    assert a.has_add_permission(rf.get("/admin/")) is False


# ---------------------------------------------------------------------------
# SiteSettingsAdmin.changeform_view — site_name blank warning
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_admin_warns_when_site_name_blank(admin_client):
    """A WARNING message appears when the admin views settings with a blank site_name."""
    SiteSettings.objects.update_or_create(pk=1, defaults={"site_name": ""})
    response = admin_client.get("/admin/core/sitesettings/1/change/")
    msgs = list(response.context["messages"])
    assert any(
        m.level == WARNING and "site name" in str(m).lower() for m in msgs
    )


@pytest.mark.django_db
def test_site_settings_admin_warns_when_contact_email_blank(admin_client):
    SiteSettings.objects.update_or_create(
        pk=1,
        defaults={"site_name": "My Studio", "contact_email": ""},
    )
    response = admin_client.get("/admin/core/sitesettings/1/change/")
    msgs = list(response.context["messages"])
    assert any(
        m.level == WARNING and "contact email" in str(m).lower() for m in msgs
    )


@pytest.mark.django_db
@override_settings(CONTACT_EMAIL="")
def test_site_settings_admin_warns_when_notification_inbox_missing(admin_client):
    SiteSettings.objects.update_or_create(
        pk=1,
        defaults={"site_name": "My Studio", "contact_email": "studio@example.com"},
    )
    response = admin_client.get("/admin/core/sitesettings/1/change/")
    msgs = list(response.context["messages"])
    assert any(
        m.level == WARNING and "notification inbox" in str(m).lower() for m in msgs
    )


@pytest.mark.django_db
def test_site_settings_admin_no_warning_when_site_name_set(admin_client):
    """No WARNING message when site_name is populated."""
    SiteSettings.objects.update_or_create(pk=1, defaults={"site_name": "My Studio"})
    response = admin_client.get("/admin/core/sitesettings/1/change/")
    msgs = list(response.context["messages"])
    assert not any(
        m.level == WARNING and "site name" in str(m).lower() for m in msgs
    )


@pytest.mark.django_db
def test_site_settings_admin_informs_when_site_name_is_long_without_nav_name_or_logo(
    admin_client,
):
    SiteSettings.objects.update_or_create(
        pk=1,
        defaults={
            "site_name": "Beaumont Whitfield Kellerman Partnership",
            "nav_name": "",
        },
    )
    response = admin_client.get("/admin/core/sitesettings/1/change/")
    msgs = list(response.context["messages"])
    assert any(
        m.level == INFO and "navigation name" in str(m).lower() for m in msgs
    )


@pytest.mark.django_db
def test_site_settings_admin_warns_when_monogram_would_collapse_to_single_letter(
    admin_client,
):
    SiteSettings.objects.update_or_create(
        pk=1,
        defaults={
            "site_name": "Supercalifragilisticexpialidocious",
            "nav_name": "",
        },
    )
    response = admin_client.get("/admin/core/sitesettings/1/change/")
    msgs = list(response.context["messages"])
    assert any(
        m.level == WARNING
        and "single letter" in str(m).lower()
        and "monogram" in str(m).lower()
        for m in msgs
    )


@pytest.mark.django_db
def test_site_settings_admin_help_text_highlights_brand_and_contact_setup(rf):
    admin_obj = SiteSettingsAdmin(SiteSettings, admin.site)
    form = admin_obj.get_form(rf.get("/admin/"))

    assert "nav_name or logo" in form.base_fields["site_name"].help_text
    assert "CONTACT_EMAIL" in form.base_fields["contact_email"].help_text
    assert "Both should be set before launch" in form.base_fields["contact_email"].help_text
    assert "serves this asset directly" in form.base_fields["og_image"].help_text
    assert "hero image source" in form.base_fields["homepage_projects_desktop_count"].help_text


@pytest.mark.django_db
@override_settings(CONTACT_EMAIL="")
def test_site_settings_admin_launch_readiness_surfaces_homepage_fallback_warning(admin_client, project):
    _populate_minimum_ready_site_and_about()

    response = admin_client.get("/admin/core/sitesettings/1/change/")

    assert response.status_code == 200
    assert b"CONTACT_EMAIL is blank" in response.content
    assert b"No featured Project records are selected" in response.content
    assert b"check_content_readiness" in response.content
