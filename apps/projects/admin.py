from django.contrib import admin
from django.utils.html import format_html

from .models import Project, ProjectImage, Testimonial

# ---------------------------------------------------------------------------
# Project + inline images
# ---------------------------------------------------------------------------


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "image_type", "caption", "alt_text", "order")
    ordering = ("order",)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        field_help = {
            "image": (
                "Upload an optimized export rather than a huge original file. "
                "Gallery images are served directly on the public site."
            ),
            "image_type": (
                "Gallery images feed the main photo sequence. All other types render in the supporting-media section."
            ),
            "order": (
                "Lower numbers appear first. If no cover image is set, the first gallery image becomes the detail hero/share fallback."
            ),
            "alt_text": (
                "Add descriptive alt text for important images. If left blank, the caption or project title is used."
            ),
        }
        for name, help_text in field_help.items():
            if name in formset.form.base_fields:
                formset.form.base_fields[name].help_text = help_text
        return formset


class TestimonialInline(admin.StackedInline):
    model = Testimonial
    extra = 0
    fields = ("name", "role", "company", "quote", "order", "active")
    ordering = ("order",)


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
    inlines = [ProjectImageInline, TestimonialInline]
    fieldsets = (
        ("Identity", {"fields": ("title", "slug", "short_description", "cover_image")}),
        ("Classification", {"fields": ("category", "status", "featured", "order")}),
        ("Metadata", {"fields": ("location", "year", "client", "area", "services_provided")}),
        ("Story", {"fields": ("overview", "challenge", "concept", "process", "outcome")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change=change, **kwargs)
        field_help = {
            "cover_image": (
                "Primary project hero and share image. Use an optimized landscape export, ideally at least 1600×900. "
                "If left blank, the detail page falls back to the first gallery image instead."
            ),
            "short_description": (
                "Shown on project cards and used as the SEO fallback description. Keep it concise so card previews stay readable."
            ),
        }
        for name, help_text in field_help.items():
            if name in form.base_fields:
                form.base_fields[name].help_text = help_text
        return form

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
    list_display = ("name", "role", "company", "project", "quote_preview", "order", "active")
    list_editable = ("order", "active")
    list_filter = ("active",)
    search_fields = ("name", "quote", "company")

    @admin.display(description="Quote")
    def quote_preview(self, obj):
        return obj.quote[:80] + "…" if len(obj.quote) > 80 else obj.quote
