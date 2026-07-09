"""Blog posts and their tags."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.common.models import UUIDTimeStampedModel


class Tag(UUIDTimeStampedModel):
    """A simple blog tag."""

    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(UUIDTimeStampedModel):
    """A blog article. Only ``published`` posts are visible publicly."""

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    cover_image = models.ImageField(upload_to="blog/covers/", blank=True, null=True)
    excerpt = models.CharField(max_length=300, blank=True)
    body = models.TextField(help_text="Markdown or rich text content.")
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="posts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        # Stamp publish time the first time a post goes live.
        if self.published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)
