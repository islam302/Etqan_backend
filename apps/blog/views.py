"""Blog ViewSet."""

from __future__ import annotations

from rest_framework import viewsets

from apps.common.permissions import IsAdminOrReadOnly

from .filters import BlogPostFilter
from .models import BlogPost
from .serializers import BlogPostSerializer


class BlogPostViewSet(viewsets.ModelViewSet):
    """Blog posts.

    Public consumers see only published posts and can filter by
    ``?tag=<slug>`` and free-text ``?search=``.
    """

    serializer_class = BlogPostSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    filterset_class = BlogPostFilter
    search_fields = ["title", "excerpt", "body"]
    ordering_fields = ["published_at", "created_at", "title"]
    ordering = ["-published_at", "-created_at"]

    def get_queryset(self):
        qs = BlogPost.objects.select_related("author").prefetch_related("tags")
        user = self.request.user
        if not (user and user.is_authenticated and user.is_staff):
            qs = qs.filter(published=True)
        return qs
