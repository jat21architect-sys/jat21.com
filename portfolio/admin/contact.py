from django.contrib import admin

from ..models import ContactInquiry

# ---------------------------------------------------------------------------
# ContactInquiry
# ---------------------------------------------------------------------------


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "project_type", "created_at", "status")
    list_filter = ("status",)
    date_hierarchy = "created_at"
    search_fields = ("name", "email", "company", "message")
    readonly_fields = (
        "name",
        "email",
        "company",
        "project_type",
        "location",
        "budget_range",
        "timeline",
        "message",
        "created_at",
    )
    list_editable = ("status",)
    fieldsets = (
        (
            "Inquiry",
            {
                "fields": (
                    "name",
                    "email",
                    "company",
                    "project_type",
                    "location",
                    "budget_range",
                    "timeline",
                    "message",
                    "created_at",
                )
            },
        ),
        ("Admin", {"fields": ("status", "notes")}),
    )

    def has_add_permission(self, request):
        return False
