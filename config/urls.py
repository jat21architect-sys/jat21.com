"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.urls import include, path
from django.views.generic import TemplateView

from apps.pages.sitemaps import StaticViewSitemap
from apps.projects.sitemaps import ProjectSitemap

_sitemaps = {
    "projects": ProjectSitemap,
    "static": StaticViewSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap_view,
        {"sitemaps": _sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("", include("apps.pages.urls")),
    path("projects/", include("apps.projects.urls")),
    path("contact/", include("apps.contact.urls")),
    path("services/", include("apps.services.urls")),
# static() is a no-op when DEBUG=False — safe to keep for local dev media serving.
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
