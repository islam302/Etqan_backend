"""Admin for projects with an inline gallery."""

from __future__ import annotations

from django.contrib import admin

from apps.common.admin import thumbnail

from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "preview", "caption", "order")
    readonly_fields = ("preview",)
    preview = thumbnail("image", height=60)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "cover_preview",
        "category",
        "client_name",
        "is_featured",
        "published",
        "order",
    )
    list_filter = ("category", "is_featured", "published")
    list_editable = ("is_featured", "published", "order")
    search_fields = ("title", "summary", "description", "client_name")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "cover_preview")
    inlines = [ProjectImageInline]
    ordering = ("order", "-created_at")

    cover_preview = thumbnail("cover_image", height=50, label="Cover")
