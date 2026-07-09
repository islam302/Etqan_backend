"""Filters for the project list endpoint."""

from __future__ import annotations

import django_filters as filters

from .models import Project


class ProjectFilter(filters.FilterSet):
    """Filter projects by category and featured flag.

    Exposes ``?category=web`` and ``?featured=true`` query params.
    """

    featured = filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Project
        fields = ["category", "featured"]
