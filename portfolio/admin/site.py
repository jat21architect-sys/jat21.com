from django.contrib import admin

from ..models import AboutProfile, Service, SiteSettings

# ---------------------------------------------------------------------------
# SiteSettings
# ---------------------------------------------------------------------------


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identity", {"fields": ("site_name", "tagline", "logo")}),
        ("Contact", {"fields": ("contact_email", "phone", "location", "address")}),
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
        ("SEO & Analytics", {"fields": ("meta_description", "og_image", "google_analytics_id")}),
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


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "summary", "order", "active")
    list_editable = ("order", "active")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "order", "active", "icon_name")}),
        ("Detail", {"fields": ("description", "who_for", "value_proposition", "deliverables")}),
    )
