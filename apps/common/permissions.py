"""Shared DRF permission classes."""

from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrReadOnly(BasePermission):
    """Allow anyone to read; only staff users may write.

    ``SAFE_METHODS`` (GET/HEAD/OPTIONS) are open to everyone so the public
    frontend can consume content, while create/update/delete require an
    authenticated staff account.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)
