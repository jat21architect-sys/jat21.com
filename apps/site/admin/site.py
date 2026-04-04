from django.conf import settings as django_settings
from django.contrib import admin, messages
from django.utils.html import format_html, format_html_join

from apps.core.templatetags.core_tags import (
    NAV_TEXT_MAX_CHARS,
    NAV_TEXT_MAX_WORDS,
    _compute_monogram,
)

from ..management.commands.check_content_readiness import collect_readiness_issues
from ..models import AboutProfile, SiteSettings

# ---------------------------------------------------------------------------
# SiteSettings
# ---------------------------------------------------------------------------


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ("launch_readiness",)
    fieldsets = (
        (
            "Launch Readiness",
            {
                "fields": ("launch_readiness",),
                "description": (
                    "This mirrors the content-readiness check used before launch. "
                    "Use it to spot setup blockers and weak homepage or brand states early."
                ),
            },
        ),
        (
            "Identity",
            {
                "fields": ("site_name", "tagline", "hero_label", "hero_compact", "nav_name", "logo", "og_image"),
                "description": (
                    "These fields shape the homepage hero, the navbar brand path, the footer identity, "
                    "and the default social share image."
                ),
            },
        ),
        (
            "Contact",
            {
                "fields": ("contact_email", "phone", "location", "address"),
                "description": (
                    "These details are public-facing. The public email shown on the site is separate from the inbox "
                    "that receives form notifications, which is configured with the CONTACT_EMAIL environment variable."
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
        (
            "Homepage — Featured Projects",
            {
                "fields": (
                    "homepage_projects_mobile_count",
                    "homepage_projects_tablet_count",
                    "homepage_projects_desktop_count",
                ),
                "description": (
                    "Controls how many homepage featured projects are shown at each screen size. "
                    "Mobile \u2264 Tablet \u2264 Desktop. Each value must be between 1 and 6."
                ),
            },
        ),
    )

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change=change, **kwargs)
        field_help = {
            "site_name": (
                "Public practice name used in the homepage hero, page-title fallback, footer, and brand accessibility label. "
                "Long names often need a nav_name or logo to stay strong in the navbar."
            ),
            "hero_label": (
                "Short descriptor above the homepage title. Leave blank to omit. "
                "If both hero_label and tagline are blank, the hero relies on the site name alone."
            ),
            "hero_compact": (
                "Use if the homepage hero looks crowded with your current site name or tagline. "
                "Check desktop, tablet, and mobile after enabling it."
            ),
            "nav_name": (
                "Shorter navbar brand override. Leave blank to let the system choose full text or a monogram automatically. "
                "Set this when the automatic fallback feels too long, too vague, or too weak."
            ),
            "logo": (
                "Replaces all text branding in the navbar. Use a clean SVG or transparent PNG that stays legible on both "
                "the transparent home header and the solid scrolled header."
            ),
            "og_image": (
                "Default share image for pages without their own image. Use a branded landscape image; 1200×630 or larger is safest. "
                "Upload an export-sized file, not a huge original, because the current site serves this asset directly."
            ),
            "contact_email": (
                "Public email shown on the site. This is separate from the inbox that receives contact-form notifications, "
                "which is configured with CONTACT_EMAIL in the environment. Both should be set before launch."
            ),
            "homepage_projects_mobile_count": (
                "Maximum featured cards shown on mobile (up to 639px). Use featured projects to control which work appears first."
            ),
            "homepage_projects_tablet_count": (
                "Maximum featured cards shown on tablet (640–959px). Use featured projects to control which work appears first."
            ),
            "homepage_projects_desktop_count": (
                "Maximum featured cards queried and shown on desktop (960px+). The first selected homepage project can also become the hero image source."
            ),
        }
        for name, help_text in field_help.items():
            if name in form.base_fields:
                form.base_fields[name].help_text = help_text
        return form

    @admin.display(description="Launch readiness")
    def launch_readiness(self, obj):
        if obj is None:
            return "Save Site Settings once to see the launch readiness summary."

        blockers, warnings = collect_readiness_issues()
        if not blockers and not warnings:
            return format_html(
                "<strong>Ready.</strong> No current launch blockers or warnings were found."
            )

        sections = []
        if blockers:
            blocker_items = format_html_join("", "<li>{}</li>", ((item,) for item in blockers))
            sections.append(
                format_html(
                    "<p><strong>{} blocking issue(s)</strong></p><ul>{}</ul>",
                    len(blockers),
                    blocker_items,
                )
            )
        if warnings:
            warning_items = format_html_join("", "<li>{}</li>", ((item,) for item in warnings))
            sections.append(
                format_html(
                    "<p><strong>{} warning(s)</strong></p><ul>{}</ul>",
                    len(warnings),
                    warning_items,
                )
            )

        return format_html(
            "{}<p><strong>Tip:</strong> Run <code>uv run python manage.py check_content_readiness</code> before launch for the same full check in the terminal.</p>",
            format_html_join("", "{}", ((section,) for section in sections)),
        )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        # Warn when site_name is blank. For GET requests we check the DB value;
        # for POST we check the submitted value so we don't fire after a successful fix.
        if request.method == "POST":
            site_name_val = request.POST.get("site_name", "").strip()
            nav_name_val = request.POST.get("nav_name", "").strip()
            logo_val = request.POST.get("logo", "") or request.FILES.get("logo")
            contact_email_val = request.POST.get("contact_email", "").strip()
        else:
            s = SiteSettings.load()
            site_name_val = s.site_name.strip()
            nav_name_val = s.nav_name.strip()
            logo_val = s.logo
            contact_email_val = s.contact_email.strip()

        site_name_blank = (
            not site_name_val
        )
        if site_name_blank:
            self.message_user(
                request,
                "Site name is blank. It appears in the page heading, navigation, and "
                "footer — set it before sharing or publishing the site.",
                level=messages.WARNING,
            )
        if not contact_email_val:
            self.message_user(
                request,
                "Public contact email is blank. The footer and contact page will not show a direct email contact until it is set.",
                level=messages.WARNING,
            )
        if not getattr(django_settings, "CONTACT_EMAIL", "").strip():
            self.message_user(
                request,
                "Notification inbox is not configured. Contact submissions will still be saved, but notification emails will not reach the practice until CONTACT_EMAIL is set in the environment.",
                level=messages.WARNING,
            )

        if not site_name_blank:
            # Warn when a long site_name could crowd the navbar and no mitigation is set.
            if len(site_name_val) > 30 and not nav_name_val and not logo_val:
                self.message_user(
                    request,
                    "Your practice name is longer than 30 characters. Consider adding a short "
                    "Navigation Name, or uploading a logo, to ensure it fits on narrow screens.",
                    level=messages.INFO,
                )
            # Warn when the auto-computed monogram collapses to a single letter.
            monogram_triggered = (
                len(site_name_val) > NAV_TEXT_MAX_CHARS
                or len(site_name_val.split()) > NAV_TEXT_MAX_WORDS
            )
            if monogram_triggered and not nav_name_val and not logo_val:
                monogram = _compute_monogram(site_name_val)
                if len(monogram) == 1:
                    self.message_user(
                        request,
                        f"The automatic nav monogram for this name would be a single letter "
                        f"(\u2018{monogram}\u2019). Consider setting a Nav Name to give visitors "
                        f"more context\u2014for example, an abbreviation like "
                        f"\u2018{monogram}CA\u2019 or a shortened version of the practice name.",
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
