"""
View tests for apps.projects: list and detail pages.
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.projects.models import Project, ProjectImage, Testimonial


@pytest.mark.django_db
def test_project_list_page(client, site_settings):
    response = client.get(reverse("projects:list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_with_category_filter(client, site_settings, project):
    url = reverse("projects:list") + "?category=housing"
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_cards_fall_back_to_first_gallery_image(client, site_settings):
    project = Project.objects.create(
        title="Gallery Fallback Project",
        slug="gallery-fallback-project",
        short_description="Uses gallery preview.",
        category="housing",
        status="completed",
    )
    gallery_image = ProjectImage.objects.create(
        project=project,
        image=SimpleUploadedFile("list-preview.jpg", b"list-preview", content_type="image/jpeg"),
        alt_text="List preview image",
        order=1,
        image_type="gallery",
    )

    response = client.get(reverse("projects:list"))

    assert response.status_code == 200
    assert gallery_image.image.url.encode() in response.content
    assert b"project-card__placeholder" not in response.content


@pytest.mark.django_db
def test_project_list_preview_images_emit_real_dimensions_when_available(
    client, site_settings, make_uploaded_image
):
    project = Project.objects.create(
        title="Sized Preview Project",
        slug="sized-preview-project",
        short_description="Uses gallery preview.",
        category="housing",
        status="completed",
    )
    gallery_image = ProjectImage.objects.create(
        project=project,
        image=make_uploaded_image("list-preview.jpg", size=(1200, 800)),
        alt_text="List preview image",
        order=1,
        image_type="gallery",
    )

    response = client.get(reverse("projects:list"))

    assert response.status_code == 200
    assert gallery_image.image.url.encode() in response.content
    assert b'decoding="async"' in response.content
    assert b'width="1200"' in response.content
    assert b'height="800"' in response.content


@pytest.mark.django_db
def test_project_list_only_shows_populated_sector_filters(client, site_settings, project):
    Project.objects.create(
        title="Civic Hall",
        slug="civic-hall",
        short_description="Public-sector project.",
        category="civic",
        status="completed",
    )
    Project.objects.create(
        title="Studio Workplace",
        slug="studio-workplace",
        short_description="Workplace project.",
        category="workplace",
        status="completed",
    )

    response = client.get(reverse("projects:list"))

    assert response.status_code == 200
    assert response.context["categories"] == [
        ("housing", "Housing"),
        ("civic", "Civic"),
        ("workplace", "Workplace"),
    ]
    assert response.context["show_category_filters"] is True


@pytest.mark.django_db
def test_project_list_four_cards_renders_uniform_grid(client, site_settings, project):
    """4-card count should use the standard 2-col grid without any orphan-centering class."""
    Project.objects.create(
        title="Civic Hall",
        slug="civic-hall",
        short_description="Public-sector project.",
        category="civic",
        status="completed",
    )
    Project.objects.create(
        title="Studio Workplace",
        slug="studio-workplace",
        short_description="Workplace project.",
        category="workplace",
        status="completed",
    )
    Project.objects.create(
        title="Housing Block",
        slug="housing-block",
        short_description="Housing project.",
        category="housing",
        status="completed",
    )

    response = client.get(reverse("projects:list"))

    assert response.status_code == 200
    assert b"projects-grid--uniform" in response.content
    assert b"projects-grid--count-4" not in response.content


@pytest.mark.django_db
def test_project_list_hides_filter_bar_when_only_one_sector_exists(client, site_settings, project):
    response = client.get(reverse("projects:list"))

    assert response.status_code == 200
    assert response.context["categories"] == [("housing", "Housing")]
    assert response.context["show_category_filters"] is False
    assert b"Filter projects by category" not in response.content


@pytest.mark.django_db
def test_project_list_redirects_legacy_category_param_to_canonical(client, site_settings, project):
    response = client.get(reverse("projects:list") + "?category=residential")

    assert response.status_code == 302
    assert response["Location"] == reverse("projects:list") + "?category=housing"


@pytest.mark.django_db
def test_project_list_redirects_removed_category_param_to_unfiltered_page(client, site_settings, project):
    response = client.get(reverse("projects:list") + "?category=interior")

    assert response.status_code == 302
    assert response["Location"] == reverse("projects:list")


@pytest.mark.django_db
def test_project_list_redirects_unknown_category_param_to_unfiltered_page(client, site_settings, project):
    response = client.get(reverse("projects:list") + "?category=competition")

    assert response.status_code == 302
    assert response["Location"] == reverse("projects:list")


@pytest.mark.django_db
def test_project_detail_page(client, site_settings, project):
    url = reverse("projects:detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_uses_first_gallery_image_for_hero_and_og_when_cover_missing(
    client, site_settings, project, make_uploaded_image
):
    gallery_image = ProjectImage.objects.create(
        project=project,
        image=make_uploaded_image("detail-hero.jpg", size=(1600, 900)),
        alt_text="Detail hero fallback",
        order=1,
        image_type="gallery",
    )

    response = client.get(reverse("projects:detail", kwargs={"slug": project.slug}))

    assert response.status_code == 200
    assert response.context["detail_media"]["image"].url == gallery_image.image.url
    assert response.context["detail_media"]["alt"] == "Detail hero fallback"
    assert response.context["detail_media"]["dimensions"] == {"width": 1600, "height": 900}
    assert response.context["og_image"] == gallery_image.image.url
    assert b"project-hero--no-image" not in response.content
    assert b'fetchpriority="high"' in response.content
    assert b'width="1600"' in response.content
    assert b'height="900"' in response.content


@pytest.mark.django_db
def test_project_detail_labels_non_gallery_media_with_truthful_section_heading(
    client, site_settings, project, make_uploaded_image
):
    ProjectImage.objects.create(
        project=project,
        image=make_uploaded_image("render.jpg", size=(900, 1200)),
        order=1,
        image_type="render",
    )

    response = client.get(reverse("projects:detail", kwargs={"slug": project.slug}))

    assert response.status_code == 200
    assert b"Drawings & Supporting Visuals" in response.content
    assert b"Drawings & Plans" not in response.content
    assert b"Render" in response.content
    assert b'decoding="async"' in response.content
    assert b'width="900"' in response.content
    assert b'height="1200"' in response.content


@pytest.mark.django_db
def test_project_detail_cta_prefills_contact_project_type_from_category(
    client, site_settings, project
):
    response = client.get(reverse("projects:detail", kwargs={"slug": project.slug}))

    assert response.status_code == 200
    assert b'href="/contact/?project_type=Housing"' in response.content


@pytest.mark.django_db
def test_project_detail_related_cards_fall_back_to_first_gallery_image(client, site_settings, project):
    related = Project.objects.create(
        title="Related Housing",
        slug="related-housing",
        short_description="Related housing project.",
        category=project.category,
        status="completed",
    )
    gallery_image = ProjectImage.objects.create(
        project=related,
        image=SimpleUploadedFile("related-preview.jpg", b"related-preview", content_type="image/jpeg"),
        alt_text="Related preview image",
        order=1,
        image_type="gallery",
    )

    url = reverse("projects:detail", kwargs={"slug": project.slug})
    response = client.get(url)

    assert response.status_code == 200
    assert gallery_image.image.url.encode() in response.content
    assert b"project-card__placeholder" not in response.content


@pytest.mark.django_db
def test_project_detail_related_preview_images_emit_real_dimensions_when_available(
    client, site_settings, project, make_uploaded_image
):
    related = Project.objects.create(
        title="Related Sized Housing",
        slug="related-sized-housing",
        short_description="Related housing project.",
        category=project.category,
        status="completed",
    )
    gallery_image = ProjectImage.objects.create(
        project=related,
        image=make_uploaded_image("related-preview.jpg", size=(1200, 800)),
        alt_text="Related preview image",
        order=1,
        image_type="gallery",
    )

    response = client.get(reverse("projects:detail", kwargs={"slug": project.slug}))

    assert response.status_code == 200
    assert gallery_image.image.url.encode() in response.content
    assert b'decoding="async"' in response.content
    assert b'width="1200"' in response.content
    assert b'height="800"' in response.content


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
      1. SiteSettings (context_processor)
      2. Project.objects.get(slug=...)
      3. gallery images
      4. drawings images
      5. related projects
      6. testimonials
    """
    url = reverse("projects:detail", kwargs={"slug": project.slug})
    with django_assert_num_queries(6):
        client.get(url)


# ---------------------------------------------------------------------------
# Project detail — og_image fallback to SiteSettings
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_detail_og_image_falls_back_to_site_settings(client, site_settings, project):
    """
    When a project has no cover image and no gallery image, og_image should
    stay absent from context so the shared site-level fallback can apply.
    """
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
