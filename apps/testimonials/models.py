"""Client testimonials."""

from __future__ import annotations

from django.db import models

from apps.common.models import UUIDTimeStampedModel


class Testimonial(UUIDTimeStampedModel):
    """A quote from a client."""

    quote = models.TextField()
    author_name = models.CharField(max_length=150)
    author_role = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self) -> str:
        return f"{self.author_name}"
