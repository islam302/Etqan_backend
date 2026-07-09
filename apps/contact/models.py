"""Contact messages submitted through the public form."""

from __future__ import annotations

from django.db import models

from apps.common.models import UUIDTimeStampedModel


class ContactMessage(UUIDTimeStampedModel):
    """A message left by a website visitor."""

    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
