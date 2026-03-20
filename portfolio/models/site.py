from django.db import models
from django.utils.text import slugify

# ---------------------------------------------------------------------------
# Singleton mixin — ensures only one row exists in the DB for "global" models
# ---------------------------------------------------------------------------


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)  # type: ignore[attr-defined]
        return obj


# ---------------------------------------------------------------------------
# SiteSettings  –  global site-wide metadata
# ---------------------------------------------------------------------------


class SiteSettings(SingletonModel):
    site_name = models.CharField(max_length=120, default="Jeannot Tsirenge")
    tagline = models.CharField(
        max_length=220,
        default="Architectural design shaped by context, clarity, and identity.",
    )
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    contact_email = models.EmailField(default="contact@jeannot-tsirenge.com")
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)

    # Social links
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    behance_url = models.URLField(blank=True, help_text="Behance profile URL.")
    issuu_url = models.URLField(blank=True, help_text="Issuu profile or publication URL.")

    # Default social share image
    og_image = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True,
        help_text="Default image used when sharing pages that have no cover image.",
    )

    # SEO
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Shown in search results. Keep under 160 characters.",
    )
    google_analytics_id = models.CharField(
        max_length=30,
        blank=True,
        help_text="GA4 Measurement ID, e.g. G-XXXXXXXXXX.",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"


# ---------------------------------------------------------------------------
# AboutProfile  –  singleton about/bio page content
# ---------------------------------------------------------------------------


class AboutProfile(SingletonModel):
    headline = models.CharField(max_length=200, blank=True)
    intro = models.TextField(
        blank=True,
        help_text="Short intro paragraph shown at the top of the About page.",
    )
    biography = models.TextField(blank=True)
    philosophy = models.TextField(blank=True)
    credentials = models.TextField(
        blank=True,
        help_text="Education, certifications, memberships — one per line.",
    )
    experience_years = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=120, blank=True)
    portrait = models.ImageField(upload_to="about/", blank=True, null=True)
    cv_file = models.FileField(upload_to="about/cv/", blank=True, null=True)

    class Meta:
        verbose_name = "About Profile"
        verbose_name_plural = "About Profile"

    def __str__(self):
        return "About Profile"


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


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

    def deliverables_list(self):
        return [d.strip() for d in self.deliverables.splitlines() if d.strip()]
