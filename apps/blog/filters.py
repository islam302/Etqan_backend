"""Filters for the blog list endpoint."""

from __future__ import annotations

import django_filters as filters

from .models import BlogPost


class BlogPostFilter(filters.FilterSet):
    """Filter posts by tag slug via ``?tag=<slug>``."""

    tag = filters.CharFilter(field_name="tags__slug", lookup_expr="iexact")

    class Meta:
        model = BlogPost
        fields = ["tag", "published"]
