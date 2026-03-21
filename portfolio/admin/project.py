from django.contrib import admin
from django.utils.html import format_html

from ..models import Project, ProjectImage, Testimonial

# ---------------------------------------------------------------------------
# Project + inline images
# ---------------------------------------------------------------------------


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "image_type", "caption", "alt_text", "order")
    ordering = ("order",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("project")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "cover_thumb",
        "title",
        "category",
        "status",
        "year",
        "location",
        "featured",
        "order",
    )
    list_display_links = ("cover_thumb", "title")
    list_editable = ("featured", "order", "year", "status")
    list_filter = ("category", "status", "featured")
    search_fields = ("title", "location", "client")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectImageInline]
    fieldsets = (
        ("Identity", {"fields": ("title", "slug", "short_description", "cover_image")}),
        ("Classification", {"fields": ("category", "status", "featured", "order")}),
        ("Metadata", {"fields": ("location", "year", "client", "area", "services_provided")}),
        ("Story", {"fields": ("overview", "challenge", "concept", "process", "outcome")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    @admin.display(description="Cover")
    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:48px;width:72px;object-fit:cover;border-radius:3px;">',
                obj.cover_image.url,
            )
        return "—"


# ---------------------------------------------------------------------------
# Testimonial
# ---------------------------------------------------------------------------


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "company", "project", "order", "active")
    list_editable = ("order", "active")
    list_filter = ("active",)
    search_fields = ("name", "quote", "company")
