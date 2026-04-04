from apps.site.models import SiteSettings


def site_settings(request):
    """Make SiteSettings available in every template as `site_settings`."""
    return {"site_settings": SiteSettings.load()}
