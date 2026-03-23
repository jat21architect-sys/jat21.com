import re

import pytest

playwright = pytest.importorskip("playwright.sync_api")
expect = playwright.expect

pytestmark = pytest.mark.e2e


def test_services_page_uses_seeded_services_and_prefills_contact_form(
    page, open_page, site_settings, seeded_services
):
    open_page("/services/")

    expect(page.get_by_role("heading", name="Services", level=1)).to_be_visible()
    expect(page.get_by_role("heading", name="Concept Design")).to_be_visible()

    concept_service = page.locator("article").filter(
        has=page.get_by_role("heading", name="Concept Design")
    )
    expect(
        concept_service.get_by_text("Early-stage design thinking")
    ).to_be_visible()

    concept_service.get_by_role("link", name="Enquire about this service").click()

    expect(page).to_have_url(re.compile(r"/contact/\?project_type=Concept(?:%20|\+)Development$"))
    expect(page.get_by_label("Project type")).to_have_value("Concept Development")
