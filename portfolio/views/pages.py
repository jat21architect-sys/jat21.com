from django.views.generic import ListView, TemplateView

from ..models import AboutProfile, Project, Service, SiteSettings, Testimonial

# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["featured_projects"] = Project.objects.filter(featured=True).order_by("order")[:6]
        # Exclude featured projects to avoid showing the same work twice on the homepage.
        ctx["all_projects"] = Project.objects.filter(featured=False).order_by("order")[:9]
        ctx["services"] = Service.objects.filter(active=True)
        ctx["testimonials"] = Testimonial.objects.filter(active=True)
        ctx["about"] = AboutProfile.load()
        site = SiteSettings.load()
        if site.og_image:
            ctx["og_image"] = site.og_image.url
        return ctx


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = AboutProfile.load()
        site = SiteSettings.load()
        if site.og_image:
            ctx["og_image"] = site.og_image.url
        return ctx


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------


class ServicesView(ListView):
    model = Service
    template_name = "services.html"
    context_object_name = "services"
    queryset = Service.objects.filter(active=True)
