"""
Model tests for apps.core: SiteSettings and AboutProfile singletons.
"""

import pytest

from apps.core.models import AboutProfile, SiteSettings

# ---------------------------------------------------------------------------
# SiteSettings singleton
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_singleton_load_creates_row():
    obj = SiteSettings.load()
    assert obj.pk == 1


@pytest.mark.django_db
def test_site_settings_singleton_only_one_row():
    SiteSettings.load()
    SiteSettings.load()  # second call must not create a second row
    assert SiteSettings.objects.count() == 1


@pytest.mark.django_db
def test_site_settings_saves_with_pk_1():
    s = SiteSettings(site_name="Test")
    s.save()
    assert s.pk == 1


# ---------------------------------------------------------------------------
# AboutProfile singleton
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_about_profile_singleton():
    a = AboutProfile.load()
    b = AboutProfile.load()
    assert a.pk == b.pk == 1
    assert AboutProfile.objects.count() == 1


# ---------------------------------------------------------------------------
# SiteSettings — social / og fields
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_site_settings_new_social_fields_default_blank():
    s = SiteSettings.load()
    assert s.behance_url == ""
    assert s.issuu_url == ""
    assert s.og_image.name is None or s.og_image.name == ""


@pytest.mark.django_db
def test_site_settings_str():
    s = SiteSettings.load()
    assert str(s) == "Site Settings"


@pytest.mark.django_db
def test_about_profile_str():
    a = AboutProfile.load()
    assert str(a) == "About Profile"
