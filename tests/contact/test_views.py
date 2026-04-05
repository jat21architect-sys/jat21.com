"""
View tests for apps.contact: contact page and success page.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_contact_page_get(client, site_settings):
    site_settings.contact_email = "contact@example.com"
    site_settings.save()
    response = client.get(reverse("contact:contact"))
    assert response.status_code == 200
    assert b"The practice reviews each enquiry directly." in response.content
    assert b"Your details are used only to review and respond to your enquiry." in response.content
    assert b"For urgent matters, email directly." in response.content


@pytest.mark.django_db
def test_contact_page_renders_stable_describedby_targets_on_clean_get(client, site_settings):
    response = client.get(reverse("contact:contact"))

    assert response.status_code == 200
    assert b'aria-describedby="id_name_error"' in response.content
    assert b'id="id_name_error"' in response.content
    assert b'aria-describedby="id_email_error"' in response.content
    assert b'id="id_email_error"' in response.content
    assert b'aria-describedby="id_message_hint id_message_error"' in response.content
    assert b'id="id_message_hint"' in response.content
    assert b'id="id_message_error"' in response.content


@pytest.mark.django_db
def test_contact_success_page(client, site_settings):
    response = client.get(reverse("contact:success"))
    assert response.status_code == 200
    assert b"Your enquiry has been received." in response.content
    assert b"The practice usually replies within two working days." in response.content
    assert b"Next step" in response.content
    assert b"Explore Projects" in response.content
    assert b"Back to Home" in response.content


@pytest.mark.django_db
def test_contact_success_page_saved_only_state(client, site_settings):
    response = client.get(reverse("contact:success") + "?delivery=saved-only")

    assert response.status_code == 200
    assert b"Your enquiry has been received and saved." in response.content
    assert b"Email notification for the practice is currently unavailable" in response.content
    assert b"response time may be longer" in response.content


@pytest.mark.django_db
def test_contact_pages_use_configured_response_time_copy(client, site_settings):
    site_settings.contact_response_time = "one week"
    site_settings.save(update_fields=["contact_response_time"])

    contact = client.get(reverse("contact:contact"))
    success = client.get(reverse("contact:success"))

    assert b"Enquiries reviewed within one week" in contact.content
    assert b"The practice usually replies within one week." in success.content


@pytest.mark.django_db
def test_contact_prefills_project_type_from_query_param(client, site_settings):
    response = client.get(reverse("contact:contact") + "?project_type=Housing")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type") == "Housing"


@pytest.mark.django_db
def test_contact_maps_legacy_project_type_query_param(client, site_settings):
    response = client.get(reverse("contact:contact") + "?project_type=Residential+Design")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type") == "Housing"


@pytest.mark.django_db
def test_contact_maps_unsupported_legacy_project_type_query_param_to_other(client, site_settings):
    response = client.get(reverse("contact:contact") + "?project_type=Concept+Development")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type") == "Other"


@pytest.mark.django_db
def test_contact_ignores_invalid_project_type_query_param(client, site_settings):
    response = client.get(reverse("contact:contact") + "?project_type=MaliciousValue")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type", "") == ""
