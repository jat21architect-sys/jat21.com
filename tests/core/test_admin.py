"""
Admin unit tests for apps.core: SiteSettings and AboutProfile singleton guards.
"""

import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.core.admin.site import AboutProfileAdmin, SiteSettingsAdmin
from apps.core.models import AboutProfile, SiteSettings


@pytest.fixture
def rf():
    return RequestFactory()


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
