import re

import pytest

from apps.contact.models import ContactInquiry

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect

pytestmark = pytest.mark.e2e


def test_contact_form_submit_reaches_success_page(
    page, open_page, app_url, site_settings, fast_contact_form
):
    open_page("/contact/")

    expect(page.get_by_role("heading", name="Let's Talk", level=1)).to_be_visible()

    page.get_by_label(re.compile("^Name")).fill("Alice Architect")
    page.get_by_label(re.compile("^Email")).fill("alice@example.com")
    page.get_by_label("Project type").select_option(label="Residential Design")
    page.get_by_label(re.compile("^Message")).fill(
        "I would like to discuss a residential project in more detail."
    )

    page.get_by_role("button", name="Send Enquiry").click()

    expect(page).to_have_url(f"{app_url}/contact/thank-you/")
    expect(page.get_by_role("heading", name="Your message is with me.", level=1)).to_be_visible()

    inquiry = ContactInquiry.objects.get(email="alice@example.com")
    assert inquiry.name == "Alice Architect"
    assert inquiry.project_type == "Residential Design"
