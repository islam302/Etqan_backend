"""Client ViewSet."""

from __future__ import annotations

from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly

from .models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """Client logos; public reads only active entries."""

    serializer_class = ClientSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering_fields = ["order", "name", "created_at"]
    ordering = ["order", "name"]

    def get_queryset(self):
        qs = Client.objects.all()
        user = self.request.user
        if not (user and user.is_authenticated and user.is_staff):
            qs = qs.filter(is_active=True)
        return qs
