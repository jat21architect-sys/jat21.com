from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return [
            "pages:home",
            "projects:list",
            "pages:about",
            "services:list",
            "contact:contact",
        ]

    def location(self, item: str) -> str:
        return reverse(item)
