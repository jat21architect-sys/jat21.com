import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect

pytestmark = pytest.mark.e2e


def test_mobile_navigation_opens_closes_and_navigates(
    mobile_page, open_page, app_url, site_settings
):
    page = mobile_page
    open_page("/")

    toggle = page.get_by_role("button", name="Toggle menu")
    projects_link = page.locator("header").get_by_role("link", name="Projects")

    expect(toggle).to_have_attribute("aria-expanded", "false")
    expect(projects_link).not_to_be_visible()

    toggle.click()

    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(projects_link).to_be_visible()
    assert page.evaluate("() => document.body.style.overflow") == "hidden"

    page.keyboard.press("Escape")

    expect(toggle).to_have_attribute("aria-expanded", "false")
    expect(projects_link).not_to_be_visible()
    assert page.evaluate("() => document.body.style.overflow") == ""

    toggle.click()
    projects_link.click()

    expect(page).to_have_url(f"{app_url}/projects/")
    expect(toggle).to_have_attribute("aria-expanded", "false")
