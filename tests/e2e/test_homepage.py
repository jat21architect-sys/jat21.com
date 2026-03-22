import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect

pytestmark = pytest.mark.e2e


def test_homepage_smoke(page, open_page, app_url, site_settings):
    open_page("/")

    expect(page.get_by_role("heading", name=site_settings.site_name, level=1)).to_be_visible()
    expect(page.get_by_role("link", name="View Projects")).to_be_visible()

    page.get_by_role("link", name="View Projects").click()

    expect(page).to_have_url(f"{app_url}/projects/")
    expect(page.get_by_role("heading", name="Projects", level=1)).to_be_visible()
