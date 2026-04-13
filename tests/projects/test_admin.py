"""
Admin unit tests for apps.projects: ProjectAdmin.cover_thumb.
"""

from unittest.mock import MagicMock

import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.projects.admin import ProjectAdmin, ProjectImageInline
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


@pytest.mark.django_db
def test_project_admin_help_text_highlights_cover_image_quality():
    pa = ProjectAdmin(Project, admin.site)
    form = pa.get_form(RequestFactory().get("/admin/"))

    assert "Primary project hero and share image" in form.base_fields["cover_image"].help_text
    assert "first gallery image instead" in form.base_fields["cover_image"].help_text


@pytest.mark.django_db
def test_project_image_inline_help_text_highlights_direct_delivery_and_ordering(project):
    inline = ProjectImageInline(Project, admin.site)
    request = RequestFactory().get("/admin/")
    request.user = MagicMock()
    request.user.has_perm.return_value = True
    formset = inline.get_formset(request, obj=project)

    assert "served directly on the public site" in formset.form.base_fields["image"].help_text  # pyright: ignore[reportGeneralTypeIssues]
    assert "first gallery image becomes the detail hero/share fallback" in formset.form.base_fields["order"].help_text  # pyright: ignore[reportGeneralTypeIssues]
