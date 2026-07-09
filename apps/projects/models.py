"""Portfolio projects and their image galleries."""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify

from apps.common.models import UUIDTimeStampedModel


class ProjectCategory(models.TextChoices):
    WEB = "web", "Web"
    MOBILE = "mobile", "Mobile"
    UIUX = "uiux", "UI/UX"
    ENTERPRISE = "enterprise", "Enterprise"


class Project(UUIDTimeStampedModel):
    """A portfolio case study."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=ProjectCategory.choices,
        default=ProjectCategory.WEB,
        db_index=True,
    )
    summary = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="projects/covers/", blank=True, null=True)
    tech_stack = models.JSONField(default=list, blank=True)
    client_name = models.CharField(max_length=150, blank=True)
    live_url = models.URLField(blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    published = models.BooleanField(default=True, db_index=True)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order", "-created_at"]
        indexes = [models.Index(fields=["category", "published"])]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProjectImage(UUIDTimeStampedModel):
    """A single gallery image belonging to a :class:`Project`."""

    project = models.ForeignKey(
        Project, related_name="gallery", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self) -> str:
        return f"{self.project.title} image #{self.pk}"
