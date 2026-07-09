"""Team members shown on the About page.

Company-wide "about" content (mission, vision, values, stats) lives on the
:class:`~apps.settings.models.SiteSettings` singleton instead of here.
"""

from __future__ import annotations

from django.db import models

from apps.common.models import UUIDTimeStampedModel


class TeamMember(UUIDTimeStampedModel):
    """A member of the ETQAN team."""

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    photo = models.ImageField(upload_to="team/", blank=True, null=True)
    bio = models.TextField(blank=True)
    # e.g. {"linkedin": "...", "github": "...", "x": "..."}
    socials = models.JSONField(default=dict, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name
