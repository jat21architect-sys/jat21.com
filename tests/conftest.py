"""
Shared pytest fixtures for the portfolio test suite.
"""

from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from apps.projects.models import Project
from apps.services.models import Service
from apps.site.models import SiteSettings


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
        category="housing",
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


@pytest.fixture
def make_uploaded_image():
    def _make(
        name: str = "test.jpg",
        size: tuple[int, int] = (1200, 900),
        color: tuple[int, int, int] = (200, 200, 200),
        image_format: str = "JPEG",
    ) -> SimpleUploadedFile:
        buffer = BytesIO()
        Image.new("RGB", size, color).save(buffer, format=image_format)
        content_type = "image/jpeg" if image_format.upper() == "JPEG" else "image/png"
        return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)

    return _make
