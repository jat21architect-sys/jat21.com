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
    expect(page.get_by_role("heading", name="Housing")).to_be_visible()
    expect(page.get_by_role("heading", name="Civic")).to_be_visible()
    expect(page.get_by_role("heading", name="Workplace")).to_be_visible()

    housing_service = page.locator("article").filter(
        has=page.get_by_role("heading", name="Housing")
    )
    expect(
        housing_service.get_by_text("Housing projects shaped by site conditions")
    ).to_be_visible()

    housing_service.get_by_role("link", name=re.compile(r"Discuss this service")).click()

    expect(page).to_have_url(re.compile(r"/contact/\?project_type=Housing$"))
    expect(page.get_by_label("Project type")).to_have_value("Housing")
