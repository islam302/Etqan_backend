"""Trusted-client logos."""

from __future__ import annotations

from django.db import models

from apps.common.models import UUIDTimeStampedModel


class Client(UUIDTimeStampedModel):
    """A client whose logo appears in the "trusted by" strip."""

    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to="clients/", blank=True, null=True)
    website = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name
