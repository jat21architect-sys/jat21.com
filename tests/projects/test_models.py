"""
Model tests for apps.projects: Project, ProjectImage, Testimonial.
"""

import pytest

from apps.projects.models import Project, ProjectImage, Testimonial


@pytest.mark.django_db
def test_project_str(project):
    assert str(project) == "Test House"


@pytest.mark.django_db
def test_project_slug_auto_generated():
    p = Project.objects.create(title="My New House")
    assert p.slug == "my-new-house"


@pytest.mark.django_db
def test_project_get_absolute_url(project):
    url = project.get_absolute_url()
    assert url == f"/projects/{project.slug}/"


@pytest.mark.django_db
def test_project_seo_title_defaults_to_title(project):
    assert project.get_seo_title() == project.title


@pytest.mark.django_db
def test_project_seo_title_uses_custom_when_set(project):
    project.seo_title = "Custom SEO Title"
    project.save()
    assert project.get_seo_title() == "Custom SEO Title"


@pytest.mark.django_db
def test_project_image_fk(project):
    img = ProjectImage.objects.create(
        project=project,
        caption="Facade view",
        order=1,
        image_type="gallery",
    )
    assert img.project == project
    assert project.images.count() == 1


# ---------------------------------------------------------------------------
# Testimonial
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_testimonial_str(db):
    t = Testimonial.objects.create(
        name="Jane Doe",
        quote="Excellent work.",
        order=1,
        active=True,
    )
    assert "Jane Doe" in str(t)


@pytest.mark.django_db
def test_testimonial_optional_project_fk(db, project):
    t = Testimonial.objects.create(
        name="Client",
        quote="Great.",
        project=project,
        order=1,
        active=True,
    )
    assert t.project == project


# ---------------------------------------------------------------------------
# ProjectImage.get_alt_text
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_image_get_alt_text_uses_alt_text_when_set(project):
    img = ProjectImage.objects.create(
        project=project,
        caption="Entrance facade",
        alt_text="View of the north-facing facade at dusk",
        order=1,
    )
    assert img.get_alt_text() == "View of the north-facing facade at dusk"


@pytest.mark.django_db
def test_project_image_get_alt_text_falls_back_to_caption(project):
    img = ProjectImage.objects.create(
        project=project,
        caption="Entrance facade",
        alt_text="",
        order=1,
    )
    assert img.get_alt_text() == "Entrance facade"


@pytest.mark.django_db
def test_project_image_get_alt_text_falls_back_to_project_title(project):
    img = ProjectImage.objects.create(
        project=project,
        caption="",
        alt_text="",
        order=1,
    )
    assert img.get_alt_text() == project.title


# ---------------------------------------------------------------------------
# Project.updated_at
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_updated_at_is_set_on_save(project):
    assert project.updated_at is not None


@pytest.mark.django_db
def test_project_updated_at_changes_on_resave(project):
    first = project.updated_at
    project.title = "Test House (Updated)"
    project.save()
    project.refresh_from_db()
    assert project.updated_at >= first


@pytest.mark.django_db
def test_project_image_str(project):
    img = ProjectImage.objects.create(project=project, order=5, caption="Roof terrace")
    assert str(img) == "Test House — image 5"
