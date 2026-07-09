"""Testimonial ViewSet."""

from __future__ import annotations

from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly

from .models import Testimonial
from .serializers import TestimonialSerializer


class TestimonialViewSet(viewsets.ModelViewSet):
    """Testimonials; public reads only active entries."""

    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["author_name", "author_role", "quote"]
    ordering_fields = ["order", "created_at"]
    ordering = ["order", "-created_at"]

    def get_queryset(self):
        qs = Testimonial.objects.all()
        user = self.request.user
        if not (user and user.is_authenticated and user.is_staff):
            qs = qs.filter(is_active=True)
        return qs
