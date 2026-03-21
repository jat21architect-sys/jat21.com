"""
Admin unit tests for apps.projects: ProjectAdmin.cover_thumb.
"""

from unittest.mock import MagicMock

import pytest
from django.contrib import admin

from apps.projects.admin import ProjectAdmin
from apps.projects.models import Project


@pytest.mark.django_db
def test_project_admin_cover_thumb_no_image(project):
    """cover_thumb returns "—" when cover_image is falsy."""
    pa = ProjectAdmin(Project, admin.site)
    mock_obj = MagicMock()
    mock_obj.cover_image = None  # falsy
    assert pa.cover_thumb(mock_obj) == "—"


@pytest.mark.django_db
def test_project_admin_cover_thumb_with_image(project):
    """cover_thumb returns an <img> tag when cover_image is set."""
    pa = ProjectAdmin(Project, admin.site)
    mock_obj = MagicMock()
    mock_obj.cover_image = MagicMock()
    mock_obj.cover_image.url = "/media/projects/cover.jpg"
    result = str(pa.cover_thumb(mock_obj))
    assert "/media/projects/cover.jpg" in result
    assert "<img" in result
