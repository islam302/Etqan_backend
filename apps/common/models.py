"""Reusable abstract model mixins shared across apps."""

from __future__ import annotations

import uuid

from django.db import models


class UUIDModel(models.Model):
    """Abstract base using a non-guessable UUID as the primary key."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Abstract base adding self-managed ``created_at``/``updated_at``."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class UUIDTimeStampedModel(UUIDModel, TimeStampedModel):
    """Combined base: UUID primary key + created/updated timestamps.

    This is the default base for all content models in the project.
    """

    class Meta(TimeStampedModel.Meta):
        abstract = True
