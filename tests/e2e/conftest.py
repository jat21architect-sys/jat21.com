"""
Shared fixtures for browser-based end-to-end tests.
"""

from __future__ import annotations

import os
from collections.abc import Callable

import pytest
from django.core.management import call_command

from apps.core.models import SiteSettings
from apps.projects.models import Project
from apps.services.models import Service

# pytest-playwright keeps an event loop around during setup, which trips
# Django's async safety guard when pytest-django creates the test database.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def app_url(live_server) -> str:
    """Expose the pytest-django live server URL to browser tests."""
    return str(live_server)


@pytest.fixture
def open_page(page, app_url) -> Callable[[str], None]:
    """Navigate without waiting on external assets such as Google Fonts."""

    def _open(path: str) -> None:
        page.goto(f"{app_url}{path}", wait_until="domcontentloaded")

    return _open


@pytest.fixture
def mobile_page(page):
    page.set_viewport_size({"width": 390, "height": 844})
    return page


@pytest.fixture
def site_settings(transactional_db):
    settings = SiteSettings.load()
    settings.site_name = "Test Site"
    settings.tagline = "Architectural design shaped by context, clarity, and identity."
    settings.contact_email = "contact@example.com"
    settings.location = "Cape Town"
    settings.save()
    return settings


@pytest.fixture
def project_factory(transactional_db) -> Callable[..., Project]:
    """Create projects that the live server can see during browser tests."""
    counter = 0

    def _make_project(**overrides) -> Project:
        nonlocal counter
        counter += 1
        defaults = {
            "title": f"Test Project {counter}",
            "short_description": "A test project for browser coverage.",
            "category": "residential",
            "status": "completed",
            "year": 2024,
            "location": "Dublin",
        }
        defaults.update(overrides)
        return Project.objects.create(**defaults)

    return _make_project


@pytest.fixture
def seeded_services(transactional_db):
    call_command("seed_services", reset=True)
    return list(Service.objects.order_by("order"))


@pytest.fixture
def fast_contact_form(settings):
    settings.CONTACT_FORM_MIN_AGE_SECONDS = 0
    return settings
