from django.db import models

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
    site_name = models.CharField(max_length=120, default="")
    tagline = models.CharField(
        max_length=220,
        default="Architectural design shaped by context, clarity, and identity.",
    )
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    contact_email = models.EmailField(default="")
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

    # SEO — global default and per-page overrides
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Default meta description (homepage and fallback). Keep under 160 characters.",
    )
    about_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the About page. Keep under 160 characters.",
    )
    services_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Services page. Keep under 160 characters.",
    )
    projects_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Projects list page. Keep under 160 characters.",
    )
    contact_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Contact page. Keep under 160 characters.",
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
    class IdentityMode(models.TextChoices):
        PERSON = "person", "Person-led practice"
        STUDIO = "studio", "Studio-led practice"

    class PortraitMode(models.TextChoices):
        PORTRAIT = "portrait", "Show portrait"
        TEXT_ONLY = "text_only", "Text only"

    identity_mode = models.CharField(
        max_length=20,
        choices=IdentityMode.choices,
        default=IdentityMode.STUDIO,
        help_text="Choose whether the About page should introduce a named principal or the studio as a whole.",
    )
    principal_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Required for person-led practices. Leave blank for studio-led practices.",
    )
    principal_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Examples: Founder and Registered Architect, Principal Architect.",
    )
    practice_structure = models.CharField(
        max_length=120,
        blank=True,
        help_text="A short truthful descriptor such as 'Solo practice' or 'Small studio'.",
    )
    one_line_practice_description = models.CharField(
        max_length=220,
        blank=True,
        help_text="Short public description shown in the hero.",
    )
    practice_summary = models.TextField(
        blank=True,
        help_text="Short factual summary of what the practice does, where it is based, and the kind of work it takes on.",
    )
    project_leadership = models.TextField(
        blank=True,
        help_text="Explain how projects are led and how consultants or collaborators are involved.",
    )
    professional_standing = models.CharField(
        max_length=220,
        blank=True,
        help_text="Registration or professional standing shown publicly on the About page.",
    )
    education = models.TextField(
        blank=True,
        help_text="Education details — one per line.",
    )
    supporting_facts = models.TextField(
        blank=True,
        help_text="Concrete supporting facts — one per line. Use factual proof, not positioning language.",
    )
    approach = models.TextField(
        blank=True,
        help_text="Keep this practical and brief — ideally 2 to 3 sentences.",
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text="Years of professional experience. This value renders publicly — 0 is a placeholder; enter the real figure.",
    )
    closing_invitation = models.CharField(
        max_length=220,
        blank=True,
        help_text="Short closing invitation shown above the contact CTA.",
    )
    portrait_mode = models.CharField(
        max_length=20,
        choices=PortraitMode.choices,
        default=PortraitMode.TEXT_ONLY,
        help_text="Use text-only mode until a real portrait is ready. Public gray placeholders are intentionally disabled.",
    )
    portrait = models.ImageField(upload_to="about/", blank=True, null=True)
    cv_file = models.FileField(upload_to="about/cv/", blank=True, null=True)

    class Meta:
        verbose_name = "About Profile"
        verbose_name_plural = "About Profile"

    def __str__(self):
        return "About Profile"

    @staticmethod
    def _lines(value: str) -> list[str]:
        return [line.strip() for line in value.splitlines() if line.strip()]

    @property
    def education_lines(self) -> list[str]:
        return self._lines(self.education)

    @property
    def supporting_fact_lines(self) -> list[str]:
        return self._lines(self.supporting_facts)

    @property
    def has_concrete_supporting_fact(self) -> bool:
        return bool(self.education_lines or self.supporting_fact_lines)
