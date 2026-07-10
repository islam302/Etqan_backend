"""Root URL configuration for the ETQAN backend."""

from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.blog.views import BlogPostViewSet
from apps.clients.views import ClientViewSet
from apps.contact.views import ContactMessageViewSet, ContactSubmitView
from apps.opinions.views import OpinionViewSet
from apps.pages.views import TeamMemberViewSet
from apps.projects.views import ProjectViewSet
from apps.services.views import ServiceViewSet
from apps.settings.views import SiteSettingsView

# ---------------------------------------------------------------------------
# API router (ViewSets)
# ---------------------------------------------------------------------------
router = DefaultRouter()
router.register("services", ServiceViewSet, basename="service")
router.register("projects", ProjectViewSet, basename="project")
router.register("blog", BlogPostViewSet, basename="blogpost")
router.register("opinions", OpinionViewSet, basename="opinion")
router.register("team", TeamMemberViewSet, basename="teammember")
router.register("clients", ClientViewSet, basename="client")
router.register("messages", ContactMessageViewSet, basename="message")

api_patterns = [
    path("auth/", include("apps.accounts.urls")),
    path("contact/", ContactSubmitView.as_view(), name="contact-submit"),
    path("settings/", SiteSettingsView.as_view(), name="site-settings"),
    # OpenAPI schema + Swagger UI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="swagger-ui",
    ),
    *router.urls,
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include((api_patterns, "api"))),
]

# Serve uploaded media in development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
