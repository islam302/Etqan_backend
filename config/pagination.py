"""Shared pagination classes."""

from __future__ import annotations

from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Page-number pagination with a client-controllable page size."""

    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100
