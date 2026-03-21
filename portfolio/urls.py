from django.urls import path

from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("projects/", views.ProjectListView.as_view(), name="project_list"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("services/", views.ServicesView.as_view(), name="services"),
    path("contact/", views.contact_view, name="contact"),
    path("contact/thank-you/", views.contact_success_view, name="contact_success"),
]
