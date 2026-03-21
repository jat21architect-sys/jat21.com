from django.views.generic import TemplateView

from projects.models import Project, Testimonial
from services.models import Service

from ..models import AboutProfile

# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["featured_projects"] = Project.objects.filter(featured=True).order_by("order")[:6]
        # Exclude featured projects to avoid showing the same work twice on the homepage.
        ctx["all_projects"] = Project.objects.filter(featured=False).order_by("order")[:9]
        ctx["services"] = Service.objects.filter(active=True)
        ctx["testimonials"] = Testimonial.objects.filter(active=True)
        ctx["about"] = AboutProfile.load()
        return ctx


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------


class AboutView(TemplateView):
    template_name = "portfolio/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = AboutProfile.load()
        return ctx
