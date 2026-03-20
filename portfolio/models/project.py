from django.db import models
from django.utils.text import slugify

# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class Project(models.Model):
    CATEGORY_CHOICES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("cultural", "Cultural"),
        ("mixed_use", "Mixed Use"),
        ("interior", "Interior Architecture"),
        ("concept", "Conceptual"),
        ("renovation", "Renovation & Adaptive Reuse"),
        ("competition", "Competition"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("in_progress", "In Progress"),
        ("concept", "Concept"),
        ("competition", "Competition Entry"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(
        max_length=300,
        help_text="One or two clear sentences shown on project cards and in search results. Under 160 characters is ideal.",
    )
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="other")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")

    # Location & metadata
    location = models.CharField(max_length=150, blank=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    client = models.CharField(max_length=150, blank=True)
    area = models.CharField(max_length=60, blank=True, help_text='e.g. "2 400 m²"')
    services_provided = models.TextField(
        blank=True,
        help_text="Scope of services delivered, e.g. 'Concept design through construction administration.' One service per line.",
    )

    # Story
    overview = models.TextField(blank=True, help_text="Project introduction paragraph.")
    challenge = models.TextField(blank=True)
    concept = models.TextField(blank=True)
    process = models.TextField(
        blank=True,
        help_text="Optional — describe the design and construction process, methods used, or team collaboration.",
    )
    outcome = models.TextField(blank=True)

    # Media
    cover_image = models.ImageField(
        upload_to="projects/covers/",
        blank=True,
        null=True,
        help_text="Recommended: at least 1600 × 900 px, JPEG or WebP. Used as the hero image and OpenGraph share image.",
    )

    # Flags
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    # SEO
    seo_title = models.CharField(
        max_length=70,
        blank=True,
        help_text="Overrides project title in browser tab and search results. Ideal length: under 60 characters.",
    )
    seo_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Overrides short description in search results. Under 160 characters.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-year", "title"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("project_detail", kwargs={"slug": self.slug})

    def get_seo_title(self):
        return self.seo_title or self.title

    def get_seo_description(self):
        return self.seo_description or self.short_description


# ---------------------------------------------------------------------------
# ProjectImage
# ---------------------------------------------------------------------------


class ProjectImage(models.Model):
    TYPE_CHOICES = [
        ("gallery", "Gallery"),
        ("plan", "Floor Plan"),
        ("section", "Section / Elevation"),
        ("sketch", "Sketch"),
        ("detail", "Detail"),
        ("render", "Render"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Descriptive alt text for screen readers. Falls back to caption if empty.",
    )
    order = models.PositiveIntegerField(default=0)
    image_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="gallery")

    class Meta:
        ordering = ["order"]
        verbose_name = "Project Image"
        verbose_name_plural = "Project Images"

    def __str__(self):
        return f"{self.project.title} — image {self.order}"

    def get_alt_text(self):
        """Return alt_text if set, falling back to caption, then project title."""
        return self.alt_text or self.caption or self.project.title


# ---------------------------------------------------------------------------
# Testimonial
# ---------------------------------------------------------------------------


class Testimonial(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    company = models.CharField(max_length=120, blank=True)
    quote = models.TextField()
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="testimonials",
    )
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} — {self.company}"
