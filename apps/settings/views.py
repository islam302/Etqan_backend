"""Public read / admin update of the site settings singleton."""

from __future__ import annotations

from rest_framework.generics import RetrieveUpdateAPIView

from apps.common.permissions import IsAdminOrReadOnly

from .models import SiteSettings
from .serializers import SiteSettingsSerializer


class SiteSettingsView(RetrieveUpdateAPIView):
    """GET the settings singleton publicly; PUT/PATCH requires staff."""

    serializer_class = SiteSettingsSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self) -> SiteSettings:
        return SiteSettings.load()
