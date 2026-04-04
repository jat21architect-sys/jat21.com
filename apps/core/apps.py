from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core_runtime"
    verbose_name = "Core Runtime"

    def ready(self):
        import apps.core.checks  # noqa: F401 - registers system checks
