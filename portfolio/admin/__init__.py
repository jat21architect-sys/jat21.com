from .contact import ContactInquiryAdmin
from .project import ProjectAdmin, ProjectImageInline, TestimonialAdmin
from .site import AboutProfileAdmin, ServiceAdmin, SiteSettingsAdmin

__all__ = [
    "SiteSettingsAdmin",
    "AboutProfileAdmin",
    "ServiceAdmin",
    "ProjectImageInline",
    "ProjectAdmin",
    "TestimonialAdmin",
    "ContactInquiryAdmin",
]
