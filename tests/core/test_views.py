"""
View tests for shared shell and product-level operational routes.
"""

import pytest
from django.test import override_settings


@pytest.mark.django_db
def test_admin_login_page_resolves(client):
    """Admin login should redirect or render — never 404/500."""
    response = client.get("/admin/login/")
    assert response.status_code in (200, 302)


@pytest.mark.django_db
def test_sitemap_returns_200(client, site_settings, project):
    """Sitemap renders with a project present so ProjectSitemap.lastmod/location are exercised."""
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert b"urlset" in response.content
    assert project.slug.encode() in response.content


@pytest.mark.django_db
def test_robots_txt_returns_200(client, site_settings):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"User-agent" in response.content
    assert b"sitemap.xml" in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/about/",
        "/privacy/",
        "/projects/",
        "/services/",
        "/contact/",
    ],
)
def test_shared_shell_landmarks_present_on_primary_public_routes(client, site_settings, path):
    response = client.get(path)

    assert response.status_code == 200
    assert b'class="skip-link"' in response.content
    assert b'id="site-header"' in response.content
    assert b'<main id="main-content">' in response.content
    assert b'class="site-footer"' in response.content


@pytest.mark.django_db
def test_skip_link_targets_main_content(client, site_settings):
    response = client.get("/")

    assert response.status_code == 200
    assert b'<a href="#main-content" class="skip-link">' in response.content
    assert b'<main id="main-content">' in response.content


@pytest.mark.django_db
def test_base_template_omits_google_analytics_script_when_measurement_id_is_blank(
    client, site_settings
):
    site_settings.google_analytics_id = ""
    site_settings.save()

    response = client.get("/")

    assert response.status_code == 200
    assert b"www.googletagmanager.com/gtag/js" not in response.content
    assert b"gtag('config'" not in response.content


@pytest.mark.django_db
def test_base_template_renders_google_analytics_script_when_measurement_id_is_set(
    client, site_settings
):
    site_settings.google_analytics_id = "G-TEST1234"
    site_settings.save()

    response = client.get("/")

    assert response.status_code == 200
    assert b"https://www.googletagmanager.com/gtag/js?id=G-TEST1234" in response.content
    assert b"gtag('config', 'G-TEST1234');" in response.content


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_404_uses_custom_template(client, site_settings):
    """A request to an unknown path should render the custom 404 template."""
    response = client.get("/this-path-does-not-exist-9x7z/")
    assert response.status_code == 404
    assert b"Page not found" in response.content
    assert b"Back to home" in response.content
