from django.contrib import admin, messages

from ..models import AboutProfile, SiteSettings

# ---------------------------------------------------------------------------
# SiteSettings
# ---------------------------------------------------------------------------


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Identity",
            {
                "fields": ("site_name", "tagline", "logo", "og_image"),
                "description": "og_image is the default image used when sharing any page on social media.",
            },
        ),
        (
            "Contact",
            {
                "fields": ("contact_email", "phone", "location", "address"),
                "description": (
                    "contact_email is shown publicly on the site. "
                    "Contact-form notification delivery is configured separately "
                    "via the CONTACT_EMAIL environment variable."
                ),
            },
        ),
        (
            "Social",
            {
                "fields": (
                    "linkedin_url",
                    "instagram_url",
                    "facebook_url",
                    "behance_url",
                    "issuu_url",
                )
            },
        ),
        (
            "SEO & Analytics",
            {
                "fields": (
                    "meta_description",
                    "about_meta_description",
                    "services_meta_description",
                    "projects_meta_description",
                    "contact_meta_description",
                    "google_analytics_id",
                )
            },
        ),
    )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        # Warn when site_name is blank. For GET requests we check the DB value;
        # for POST we check the submitted value so we don't fire after a successful fix.
        site_name_blank = (
            not request.POST.get("site_name")
            if request.method == "POST"
            else not SiteSettings.load().site_name
        )
        if site_name_blank:
            self.message_user(
                request,
                "Site name is blank. It appears in the page heading, navigation, and "
                "footer — set it before sharing or publishing the site.",
                level=messages.WARNING,
            )
        return super().changeform_view(request, object_id, form_url, extra_context)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


# ---------------------------------------------------------------------------
# AboutProfile
# ---------------------------------------------------------------------------


@admin.register(AboutProfile)
class AboutProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "identity_mode",
                    "principal_name",
                    "principal_title",
                    "practice_structure",
                    "one_line_practice_description",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "practice_summary",
                    "project_leadership",
                    "approach",
                    "closing_invitation",
                ),
                "description": (
                    "Keep the About page factual. Practice summary explains what the practice "
                    "does; project leadership explains how work is led and where consultants fit in."
                ),
            },
        ),
        (
            "Professional Profile",
            {
                "fields": (
                    "professional_standing",
                    "education",
                    "supporting_facts",
                    "experience_years",
                ),
                "description": (
                    "Use concrete facts only. The public profile renders only when location, "
                    "professional standing, years in practice, and at least one supporting fact are present."
                ),
            },
        ),
        (
            "Files & Display",
            {
                "fields": ("portrait_mode", "portrait", "cv_file"),
                "description": (
                    "Text-only mode is allowed, but the public page will not show a gray portrait placeholder."
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not AboutProfile.objects.exists()
