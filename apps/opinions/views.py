"""Opinion ViewSet."""

from __future__ import annotations

from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly

from .models import Opinion
from .serializers import OpinionSerializer


class OpinionViewSet(viewsets.ModelViewSet):
    """Opinions; public reads only active entries."""

    serializer_class = OpinionSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["author_name", "author_role", "quote"]
    ordering_fields = ["order", "created_at"]
    ordering = ["order", "-created_at"]

    def get_queryset(self):
        qs = Opinion.objects.all()
        user = self.request.user
        if not (user and user.is_authenticated and user.is_staff):
            qs = qs.filter(is_active=True)
        return qs
