from django.db import models
from django.utils.text import slugify

CONTACT_PROJECT_TYPE_MAP = {
    "residential-design": "Residential Design",
    "renovation-adaptive-reuse": "Renovation / Adaptive Reuse",
    "interior-architecture": "Interior Architecture",
    "concept-design": "Concept Development",
}


class Service(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    who_for = models.CharField(max_length=250, blank=True)
    value_proposition = models.TextField(blank=True)
    deliverables = models.TextField(
        blank=True,
        help_text="One deliverable per line.",
    )
    icon_name = models.CharField(
        max_length=60,
        blank=True,
        help_text="Optional icon identifier (e.g. 'pen-ruler', 'building').",
    )
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def contact_project_type(self) -> str:
        return CONTACT_PROJECT_TYPE_MAP.get(self.slug, "Other")

    def deliverables_list(self):
        return [d.strip() for d in self.deliverables.splitlines() if d.strip()]
