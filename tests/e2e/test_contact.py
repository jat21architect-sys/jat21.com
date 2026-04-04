import re

import pytest

from apps.contact.models import ContactInquiry

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect

pytestmark = pytest.mark.e2e


def test_contact_form_submit_reaches_success_page(
    page, open_page, app_url, site_settings, fast_contact_form
):
    fast_contact_form.CONTACT_EMAIL = "notify@example.com"
    fast_contact_form.DEFAULT_FROM_EMAIL = "no-reply@example.com"
    open_page("/contact/")

    expect(page.get_by_role("heading", name="Let's Talk", level=1)).to_be_visible()

    page.get_by_label(re.compile("^Name")).fill("Alice Architect")
    page.get_by_label(re.compile("^Email")).fill("alice@example.com")
    page.get_by_label("Project type").select_option(label="Housing")
    page.get_by_label(re.compile("^Message")).fill(
        "I would like to discuss a residential project in more detail."
    )

    page.get_by_role("button", name="Send Enquiry").click()

    expect(page).to_have_url(f"{app_url}/contact/thank-you/?delivery=sent")
    expect(page.get_by_role("heading", name="Your enquiry has been received.", level=1)).to_be_visible()

    inquiry = ContactInquiry.objects.get(email="alice@example.com")
    assert inquiry.name == "Alice Architect"
    assert inquiry.project_type == "Housing"


def test_contact_form_invalid_submit_prioritizes_field_errors_and_focuses_name(
    page, open_page, site_settings
):
    open_page("/contact/")

    page.get_by_role("button", name="Send Enquiry").click()

    expect(page.get_by_text("Please wait a moment and try again.")).to_have_count(0)
    expect(page.locator("#id_name")).to_be_focused()
