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
    # Unique handle. Nullable so social sign-ups (which may not supply one) and
    # existing flows work; the API auto-generates one when omitted.
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Public handle; may be used to log in instead of email.",
    )
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
        return self.name or (self.username or self.email.split("@")[0])

    def get_full_name(self) -> str:
        return self.name or self.email


class SocialAccount(models.Model):
    """Links a third-party identity (Google/Apple/Facebook) to a local user.

    Uniqueness on ``(provider, uid)`` ensures each external identity maps to a
    single account and repeated logins resolve to the same user.
    """

    class Provider(models.TextChoices):
        GOOGLE = "google", "Google"
        APPLE = "apple", "Apple"
        FACEBOOK = "facebook", "Facebook"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "accounts.User", related_name="social_accounts", on_delete=models.CASCADE
    )
    provider = models.CharField(max_length=20, choices=Provider.choices, db_index=True)
    uid = models.CharField(max_length=255, help_text="Provider's stable user id.")
    extra_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "social account"
        verbose_name_plural = "social accounts"
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "uid"], name="unique_provider_uid"
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_provider_display()}:{self.uid}"
