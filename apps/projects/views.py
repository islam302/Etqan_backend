"""Project portfolio ViewSet."""

from __future__ import annotations

from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly

from .filters import ProjectFilter
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """Portfolio projects.

    Public consumers see only published projects and can filter by
    ``?category=``, ``?featured=true`` and free-text ``?search=``.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filterset_class = ProjectFilter
    search_fields = ["title", "summary", "description", "client_name"]
    ordering_fields = ["order", "created_at", "title"]
    ordering = ["order", "-created_at"]

    def get_queryset(self):
        qs = Project.objects.prefetch_related("gallery")
        user = self.request.user
        if not (user and user.is_authenticated and user.is_staff):
            qs = qs.filter(published=True)
        return qs
