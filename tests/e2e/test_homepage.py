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


def test_homepage_reduced_motion_disables_hero_animation_and_transition(
    page, open_page, site_settings
):
    page.emulate_media(reduced_motion="reduce")
    open_page("/")

    styles = page.locator(".hero__scroll-line").evaluate(
        """() => {
            const scrollLine = document.querySelector('.hero__scroll-line');
            const bg = document.querySelector('.hero__bg');
            const scrollStyles = window.getComputedStyle(scrollLine);
            const bgStyles = window.getComputedStyle(bg);
            return {
                animationName: scrollStyles.animationName,
                transitionDuration: bgStyles.transitionDuration,
            };
        }"""
    )

    assert styles["animationName"] == "none"
    assert styles["transitionDuration"] == "0s"


def test_homepage_scroll_affordance_hides_at_mobile_breakpoint(page, open_page, site_settings):
    page.set_viewport_size({"width": 768, "height": 1024})
    open_page("/")

    desktop_display = page.locator(".hero__scroll").evaluate(
        "(el) => window.getComputedStyle(el).display"
    )
    assert desktop_display != "none"

    page.set_viewport_size({"width": 390, "height": 844})
    page.reload(wait_until="domcontentloaded")

    mobile_display = page.locator(".hero__scroll").evaluate(
        "(el) => window.getComputedStyle(el).display"
    )
    assert mobile_display == "none"
