"""Service offerings shown on the marketing site."""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify

from apps.common.models import UUIDTimeStampedModel


class Service(UUIDTimeStampedModel):
    """A single service the agency offers (e.g. Web Development)."""

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    long_description = models.TextField(blank=True)
    # An icon key/name the frontend maps to its own icon set.
    icon = models.CharField(max_length=80, blank=True)
    # A simple list of feature strings, e.g. ["Responsive", "SEO"].
    features = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
