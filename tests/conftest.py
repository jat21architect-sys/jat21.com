"""
Shared pytest fixtures for the jeannote test suite.
"""

import pytest

from portfolio.models import SiteSettings
from projects.models import Project
from services.models import Service


@pytest.fixture
def site_settings(db):
    """Ensure a SiteSettings singleton exists."""
    return SiteSettings.objects.get_or_create(
        pk=1,
        defaults={"site_name": "Test Site"},
    )[0]


@pytest.fixture
def project(db):
    """A minimal published project for view tests."""
    return Project.objects.create(
        title="Test House",
        slug="test-house",
        short_description="A test project.",
        category="residential",
        status="completed",
        year=2024,
        location="Dublin",
    )


@pytest.fixture
def service(db):
    """A minimal active service."""
    return Service.objects.create(
        title="Architectural Design",
        slug="architectural-design",
        summary="Full design service.",
        order=1,
        active=True,
    )
