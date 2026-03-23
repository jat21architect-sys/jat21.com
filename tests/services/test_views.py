"""
View tests for apps.services: services list page.
"""

import pytest
from django.urls import reverse

from apps.services.models import Service


@pytest.mark.django_db
def test_services_page(client, site_settings):
    response = client.get(reverse("services:list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_services_page_uses_mapped_contact_project_type_query_param(client, site_settings):
    Service.objects.create(
        title="Concept Design",
        slug="concept-design",
        summary="Early-stage design thinking.",
        order=1,
        active=True,
    )

    response = client.get(reverse("services:list"))

    assert response.status_code == 200
    assert b"?project_type=Concept%20Development" in response.content
