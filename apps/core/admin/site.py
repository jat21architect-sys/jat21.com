from django.contrib import admin

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

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


# ---------------------------------------------------------------------------
# AboutProfile
# ---------------------------------------------------------------------------


@admin.register(AboutProfile)
class AboutProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Header", {"fields": ("headline", "intro")}),
        ("Content", {"fields": ("biography", "philosophy", "credentials")}),
        ("Details", {"fields": ("experience_years", "location")}),
        ("Files", {"fields": ("portrait", "cv_file")}),
    )

    def has_add_permission(self, request):
        return not AboutProfile.objects.exists()
