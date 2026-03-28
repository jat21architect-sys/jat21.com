from django.views.generic import TemplateView

from apps.core.models import AboutProfile, SiteSettings
from apps.projects.models import Project


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        featured_projects = list(
            Project.objects.with_preview_media().filter(featured=True).order_by("order")[:4]
        )
        remaining_slots = max(0, 4 - len(featured_projects))
        supporting_projects = list(
            Project.objects.with_preview_media()
            .filter(featured=False)
            .order_by("order")[:remaining_slots]
        )
        homepage_projects = featured_projects + supporting_projects
        ctx["homepage_projects"] = homepage_projects
        ctx["hero_project"] = homepage_projects[0] if homepage_projects else None
        ctx["home_coda_project"] = (
            homepage_projects[-1] if len(homepage_projects) > 1 else ctx["hero_project"]
        )
        ctx["about"] = AboutProfile.load()
        return ctx


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = AboutProfile.load()
        site = SiteSettings.load()

        show_portrait = (
            profile.portrait_mode == AboutProfile.PortraitMode.PORTRAIT and bool(profile.portrait)
        )
        hero_title = site.site_name or "About"
        hero_meta = ""

        if (
            profile.identity_mode == AboutProfile.IdentityMode.PERSON
            and profile.principal_name
        ):
            hero_title = profile.principal_name
            hero_meta = ", ".join(
                part for part in [profile.principal_title, site.site_name] if part
            )
        elif profile.public_practice_structure:
            hero_meta = profile.public_practice_structure

        show_professional_profile = bool(
            site.location
            and profile.public_professional_standing
            and profile.experience_years
            and profile.has_concrete_supporting_fact
        )

        ctx["profile"] = profile
        ctx["about_hero_title"] = hero_title
        ctx["about_hero_meta"] = hero_meta
        ctx["show_about_portrait"] = show_portrait
        ctx["show_professional_profile"] = show_professional_profile
        ctx["about_public_location"] = site.location
        return ctx


class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"
