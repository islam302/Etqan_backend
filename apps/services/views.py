"""ViewSet exposing services to the public and admins."""

from __future__ import annotations

from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly

from .models import Service
from .serializers import ServiceSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    """List/retrieve services publicly; create/update/delete require staff.

    Public consumers only ever see active services; staff see everything.
    """

    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filterset_fields = ["is_active"]
    search_fields = ["title", "short_description", "long_description"]
    ordering_fields = ["order", "title", "created_at"]
    ordering = ["order", "title"]

    def get_queryset(self):
        qs = Service.objects.all()
        user = self.request.user
        if not (user and user.is_authenticated and user.is_staff):
            qs = qs.filter(is_active=True)
        return qs
