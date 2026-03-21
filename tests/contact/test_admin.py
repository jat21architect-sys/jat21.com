"""
Admin unit tests for apps.contact: ContactInquiry admin restrictions.
"""

import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.contact.admin import ContactInquiryAdmin
from apps.contact.models import ContactInquiry


@pytest.mark.django_db
def test_contact_inquiry_admin_has_no_add_permission(db):
    a = ContactInquiryAdmin(ContactInquiry, admin.site)
    request = RequestFactory().get("/admin/")
    assert a.has_add_permission(request) is False
