from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Project


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.all().order_by("order", "-year")

    def lastmod(self, obj: Project):
        return obj.updated_at

    def location(self, obj: Project) -> str:
        return obj.get_absolute_url()


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ["home", "project_list", "about", "services", "contact"]

    def location(self, item: str) -> str:
        return reverse(f"portfolio:{item}")
