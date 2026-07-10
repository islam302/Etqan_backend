"""Client opinions (formerly "testimonials")."""

from __future__ import annotations

from django.db import models

from apps.common.models import UUIDTimeStampedModel


class Opinion(UUIDTimeStampedModel):
    """A quote/opinion from a client."""

    quote = models.TextField()
    author_name = models.CharField(max_length=150)
    author_role = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to="opinions/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "opinion"
        verbose_name_plural = "opinions"

    def __str__(self) -> str:
        return f"{self.author_name}"
