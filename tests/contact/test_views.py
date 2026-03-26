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
    assert b"Your details are used only to respond to your enquiry." in response.content
    assert b"For urgent enquiries, email directly." in response.content


@pytest.mark.django_db
def test_contact_success_page(client, site_settings):
    response = client.get(reverse("contact:success"))
    assert response.status_code == 200
    assert b"Your enquiry has been received." in response.content
    assert b"The practice will review your message and follow up by email within two working days." in response.content


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
