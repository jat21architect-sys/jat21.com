from django.apps import AppConfig


class SiteConfigApp(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.site"
    label = "core"
    verbose_name = "Site Configuration"
