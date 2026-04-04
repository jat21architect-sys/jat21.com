from typing import Any, TypedDict

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import DetailView, ListView

from .models import Project

# ---------------------------------------------------------------------------
# Project list
# ---------------------------------------------------------------------------


class ProjectListView(ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_public_queryset(self):
        return Project.objects.with_preview_media().all().order_by("order", "-year")

    def get_available_categories(self, queryset):
        available_values = set(queryset.values_list("category", flat=True))
        return [
            (value, label)
            for value, label in Project.CATEGORY_CHOICES
            if value in available_values
        ]

    def build_category_redirect(self, category=""):
        base_url = reverse("projects:list")
        if not category:
            return HttpResponseRedirect(base_url)

        params = self.request.GET.copy()
        params["category"] = category
        return HttpResponseRedirect(f"{base_url}?{params.urlencode()}")

    def dispatch(self, request, *args, **kwargs):
        self.public_projects = self.get_public_queryset()
        self.available_categories = self.get_available_categories(self.public_projects)
        self.available_category_values = {value for value, _ in self.available_categories}

        requested_category = request.GET.get("category", "")
        if requested_category in Project.LEGACY_CATEGORY_REDIRECTS:
            canonical_category = Project.LEGACY_CATEGORY_REDIRECTS[requested_category]
            if canonical_category in self.available_category_values:
                return self.build_category_redirect(canonical_category)
            return self.build_category_redirect()

        if requested_category:
            if requested_category in Project.REMOVED_CATEGORY_PARAMS:
                return self.build_category_redirect()
            if requested_category not in Project.CANONICAL_CATEGORY_VALUES:
                return self.build_category_redirect()
            if requested_category not in self.available_category_values:
                return self.build_category_redirect()

        self.active_category = requested_category
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = self.public_projects.all()
        if self.active_category:
            qs = qs.filter(category=self.active_category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = self.available_categories
        ctx["active_category"] = self.active_category
        ctx["show_category_filters"] = len(self.available_categories) > 1
        return ctx


# ---------------------------------------------------------------------------
# Project detail
# ---------------------------------------------------------------------------


class DetailMedia(TypedDict):
    image: Any | None
    alt: str
    dimensions: Any | None


def _resolve_detail_media(project: Project, gallery: list[Any]) -> DetailMedia:
    if project.cover_image:
        return {
            "image": project.cover_image,
            "alt": project.title,
            "dimensions": project.cover_image_dimensions,
        }

    first_gallery = gallery[0] if gallery else None
    if first_gallery:
        return {
            "image": first_gallery.image,
            "alt": first_gallery.get_alt_text(),
            "dimensions": first_gallery.dimensions,
        }

    return {"image": None, "alt": project.title, "dimensions": None}


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object
        gallery = list(project.images.filter(image_type="gallery"))
        drawings = list(project.images.exclude(image_type="gallery"))
        detail_media = _resolve_detail_media(project, gallery)

        ctx["gallery"] = gallery
        ctx["drawings"] = drawings
        ctx["detail_media"] = detail_media
        ctx["related"] = (
            Project.objects.with_preview_media()
            .filter(category=project.category)
            .exclude(pk=project.pk)
            .order_by("order")[:3]
        )
        ctx["testimonials"] = project.testimonials.filter(active=True)
        if detail_media["image"]:
            ctx["og_image"] = detail_media["image"].url
        return ctx
