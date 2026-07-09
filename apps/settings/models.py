"""Global, editable site settings stored as a single row (singleton)."""

from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import UUIDTimeStampedModel


class SiteSettings(UUIDTimeStampedModel):
    """Singleton holding site-wide marketing content and contact details.

    Enforced to a single row: the ``pk`` is pinned to a fixed UUID sentinel
    so there is only ever one instance. Use :meth:`load` to fetch-or-create it.
    """

    # Fixed primary key so the singleton is always addressable / upsertable.
    SINGLETON_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

    # Hero
    hero_title = models.CharField(
        max_length=200, default="Building the Future of Software"
    )
    hero_subtitle = models.CharField(max_length=300, blank=True)
    announcement_text = models.CharField(max_length=255, blank=True)

    # Company / About
    company_about = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    # List of {"title": ..., "description": ...}
    values = models.JSONField(default=list, blank=True)

    # Stats, e.g. {"projects": 120, "clients": 45, "retention": 98, "awards": 12}
    stats = models.JSONField(default=dict, blank=True)

    # Contact
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=255, blank=True)
    # e.g. {"linkedin": "...", "x": "...", "github": "...", "instagram": "..."}
    social_links = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self) -> str:
        return "Site settings"

    def save(self, *args, **kwargs) -> None:
        self.pk = self.SINGLETON_ID
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):  # noqa: ANN002, ANN003
        raise ValidationError("The site settings singleton cannot be deleted.")

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=cls.SINGLETON_ID)
        return obj
