import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect

pytestmark = pytest.mark.e2e


def test_header_gains_and_loses_scrolled_state_on_scroll(page, open_page, site_settings):
    open_page("/")

    header = page.locator("#site-header")

    assert header.evaluate("(el) => el.classList.contains('scrolled')") is False

    page.evaluate("window.scrollTo(0, 120)")
    page.wait_for_function(
        "() => document.getElementById('site-header')?.classList.contains('scrolled')"
    )
    assert header.evaluate("(el) => el.classList.contains('scrolled')") is True

    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_function(
        "() => !document.getElementById('site-header')?.classList.contains('scrolled')"
    )
    assert header.evaluate("(el) => el.classList.contains('scrolled')") is False


def test_keyboard_focus_uses_shared_focus_visible_outline(page, open_page, site_settings):
    open_page("/")

    skip_link = page.get_by_role("link", name="Skip to main content")

    page.keyboard.press("Tab")

    expect(skip_link).to_be_focused()
    styles = skip_link.evaluate(
        """(el) => {
            const s = window.getComputedStyle(el);
            return {
                outlineStyle: s.outlineStyle,
                outlineWidth: s.outlineWidth,
                outlineOffset: s.outlineOffset,
            };
        }"""
    )

    assert styles == {
        "outlineStyle": "solid",
        "outlineWidth": "2px",
        "outlineOffset": "3px",
    }


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


def test_mobile_navigation_keyboard_focus_moves_into_menu_and_returns_on_escape(
    mobile_page, open_page, site_settings
):
    page = mobile_page
    open_page("/")

    toggle = page.get_by_role("button", name="Toggle menu")
    projects_link = page.locator("header").get_by_role("link", name="Projects")

    toggle.focus()
    page.keyboard.press("Enter")

    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(projects_link).to_be_focused()
    assert page.evaluate("() => document.body.style.overflow") == "hidden"

    page.keyboard.press("Shift+Tab")
    expect(toggle).to_be_focused()

    page.keyboard.press("Escape")

    expect(toggle).to_have_attribute("aria-expanded", "false")
    expect(toggle).to_be_focused()
    assert page.evaluate("() => document.body.style.overflow") == ""


def test_mobile_navigation_recovers_when_viewport_crosses_breakpoint(
    mobile_page, open_page, site_settings
):
    page = mobile_page
    open_page("/")

    toggle = page.get_by_role("button", name="Toggle menu")
    toggle_state = page.locator(".nav__toggle")
    projects_link = page.locator("header").get_by_role("link", name="Projects")

    toggle.click()

    expect(toggle).to_have_attribute("aria-expanded", "true")
    expect(projects_link).to_be_visible()
    assert page.evaluate("() => document.body.style.overflow") == "hidden"

    page.set_viewport_size({"width": 768, "height": 1024})
    page.wait_for_function(
        """() => {
            const toggle = document.querySelector('.nav__toggle');
            const header = document.getElementById('site-header');
            return (
                toggle?.getAttribute('aria-expanded') === 'false' &&
                document.body.style.overflow === '' &&
                !header?.classList.contains('nav-open')
            );
        }"""
    )

    expect(toggle_state).to_have_attribute("aria-expanded", "false")
    expect(projects_link).to_be_visible()
    assert page.evaluate("() => document.body.style.overflow") == ""


def test_contact_nav_cta_keeps_desktop_style_and_resets_in_mobile_overlay(
    page, open_page, site_settings
):
    open_page("/contact/")

    contact_link = page.locator("header").get_by_role("link", name="Contact")

    desktop_styles = contact_link.evaluate(
        """(el) => {
            const s = window.getComputedStyle(el);
            return {
                className: el.className,
                borderTopWidth: s.borderTopWidth,
                borderTopStyle: s.borderTopStyle,
                fontFamily: s.fontFamily,
            };
        }"""
    )

    assert "is-active" in desktop_styles["className"]
    assert desktop_styles["borderTopWidth"] == "1px"
    assert desktop_styles["borderTopStyle"] == "solid"
    assert "DM Sans" in desktop_styles["fontFamily"]

    page.set_viewport_size({"width": 390, "height": 844})
    page.reload(wait_until="domcontentloaded")

    toggle = page.get_by_role("button", name="Toggle menu")
    toggle.click()
    expect(toggle).to_have_attribute("aria-expanded", "true")

    mobile_styles = contact_link.evaluate(
        """(el) => {
            const s = window.getComputedStyle(el);
            return {
                borderTopWidth: s.borderTopWidth,
                borderTopStyle: s.borderTopStyle,
                fontFamily: s.fontFamily,
                fontSize: s.fontSize,
            };
        }"""
    )

    assert mobile_styles["borderTopWidth"] == "0px"
    assert mobile_styles["borderTopStyle"] == "none"
    assert "Cormorant Garamond" in mobile_styles["fontFamily"]
    assert mobile_styles["fontSize"] == "32px"


def test_tablet_navigation_uses_inline_links(open_page, page, site_settings):
    page.set_viewport_size({"width": 768, "height": 1024})
    open_page("/")

    toggle = page.get_by_role("button", name="Toggle menu")
    projects_link = page.locator("header").get_by_role("link", name="Projects")
    contact_link = page.locator("header").get_by_role("link", name="Contact")

    expect(toggle).not_to_be_visible()
    expect(projects_link).to_be_visible()
    expect(contact_link).to_be_visible()
