"""Custom user model using email as the unique identifier."""

from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Application user. Authenticates with ``email`` + ``password``.

    ``is_staff`` grants access to the Django admin and write access to the
    content API; ``is_superuser`` grants all permissions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("email address", unique=True, db_index=True)
    name = models.CharField(max_length=150, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into the admin site.",
    )

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = ["name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    @property
    def is_admin(self) -> bool:
        """Backwards-compatible alias used across the API/admin."""
        return self.is_staff or self.is_superuser

    def get_short_name(self) -> str:
        return self.name or self.email.split("@")[0]

    def get_full_name(self) -> str:
        return self.name or self.email
