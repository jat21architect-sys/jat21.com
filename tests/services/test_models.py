"""
Model tests for apps.services: Service.
"""

import pytest

from apps.services.models import Service


@pytest.mark.django_db
def test_service_str(service):
    assert str(service) == "Architectural Design"


@pytest.mark.django_db
def test_service_slug_auto_generated():
    s = Service.objects.create(title="Urban Planning", order=10, active=True)
    assert s.slug == "urban-planning"


@pytest.mark.django_db
def test_service_deliverables_list(db):
    s = Service.objects.create(
        title="Test Service",
        order=1,
        active=True,
        deliverables="Item one\nItem two\nItem three",
    )
    items = s.deliverables_list()
    assert len(items) == 3
    assert "Item one" in items


@pytest.mark.django_db
def test_service_contact_project_type_mapping():
    concept = Service.objects.create(
        title="Concept Design",
        slug="concept-design",
        summary="Early-stage design thinking.",
        order=1,
        active=True,
    )
    renovation = Service.objects.create(
        title="Renovation & Adaptive Reuse",
        slug="renovation-adaptive-reuse",
        summary="Existing building work.",
        order=2,
        active=True,
    )
    custom = Service.objects.create(
        title="Feasibility Review",
        slug="feasibility-review",
        summary="A custom service.",
        order=3,
        active=True,
    )

    assert concept.contact_project_type == "Concept Development"
    assert renovation.contact_project_type == "Renovation / Adaptive Reuse"
    assert custom.contact_project_type == "Other"
