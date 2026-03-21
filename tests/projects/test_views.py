"""
View tests for apps.projects: list and detail pages.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from django.urls import reverse

from apps.projects.models import Project, Testimonial


@pytest.mark.django_db
def test_project_list_page(client, site_settings):
    response = client.get(reverse("projects:list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_with_category_filter(client, site_settings, project):
    url = reverse("projects:list") + "?category=residential"
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_page(client, site_settings, project):
    url = reverse("projects:detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_404_for_unknown_slug(client, site_settings):
    url = reverse("projects:detail", kwargs={"slug": "does-not-exist"})
    response = client.get(url)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Project detail — context enrichments
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_detail_context_has_testimonials_key(client, site_settings, project):
    url = reverse("projects:detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 200
    assert "testimonials" in response.context


@pytest.mark.django_db
def test_project_detail_context_shows_linked_testimonials(client, site_settings, project):
    Testimonial.objects.create(
        name="Happy Client",
        quote="Exceptional design.",
        project=project,
        order=1,
        active=True,
    )
    url = reverse("projects:detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.context["testimonials"].count() == 1


@pytest.mark.django_db
def test_project_detail_context_excludes_inactive_testimonials(client, site_settings, project):
    Testimonial.objects.create(
        name="Inactive Client",
        quote="Redacted.",
        project=project,
        order=1,
        active=False,
    )
    url = reverse("projects:detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.context["testimonials"].count() == 0


# ---------------------------------------------------------------------------
# Project detail — query count regression
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_detail_query_count(client, site_settings, project, django_assert_num_queries):
    """
    Regression guard for the N+1 fix on ProjectDetailView.

    Expected queries for a project with no cover_image, no gallery/drawings,
    no testimonials, no related projects:
      1. session load
      2. SiteSettings (context_processor)
      3. Project.objects.get(slug=...)
      4. gallery images (select_related)
      5. drawings images (select_related)
      6. related projects
      7. testimonials
    """
    url = reverse("projects:detail", kwargs={"slug": project.slug})
    with django_assert_num_queries(7):
        client.get(url)


# ---------------------------------------------------------------------------
# Project detail — og_image fallback to SiteSettings
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_detail_og_image_falls_back_to_site_settings(client, site_settings, project):
    """
    When a project has no cover_image, og_image in context should come from
    SiteSettings.og_image if one is set. When neither is set, og_image should
    not be in the context at all.
    """
    # No cover image on the project fixture, no og_image on site_settings:
    # og_image key should be absent from context.
    url = reverse("projects:detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 200
    assert "og_image" not in response.context


@pytest.mark.django_db
def test_project_detail_og_image_set_when_cover_exists(client, site_settings, project):
    """og_image is added to context when the project has a cover_image."""
    mock_file = MagicMock()
    mock_file.url = "/media/projects/cover.jpg"
    with patch.object(Project, "cover_image", new_callable=PropertyMock) as mock_cover:
        mock_cover.return_value = mock_file
        url = reverse("projects:detail", kwargs={"slug": project.slug})
        response = client.get(url)
    assert response.status_code == 200
    assert response.context["og_image"] == "/media/projects/cover.jpg"
