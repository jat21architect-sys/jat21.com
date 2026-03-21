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

    def get_queryset(self):
        qs = Project.objects.all().order_by("order", "-year")
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Project.CATEGORY_CHOICES
        ctx["active_category"] = self.request.GET.get("category", "")
        return ctx


# ---------------------------------------------------------------------------
# Project detail
# ---------------------------------------------------------------------------


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.object
        ctx["gallery"] = project.images.filter(image_type="gallery").select_related("project")
        ctx["drawings"] = project.images.exclude(image_type="gallery").select_related("project")
        ctx["related"] = (
            Project.objects.filter(category=project.category)
            .exclude(pk=project.pk)
            .order_by("order")[:3]
        )
        ctx["testimonials"] = project.testimonials.filter(active=True)
        if project.cover_image:
            ctx["og_image"] = project.cover_image.url
        return ctx
