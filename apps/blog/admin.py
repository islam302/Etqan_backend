"""Admin for blog posts and tags."""

from __future__ import annotations

from django.contrib import admin

from apps.common.admin import thumbnail

from .models import BlogPost, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "cover_preview", "author", "published", "published_at")
    list_filter = ("published", "tags", "author")
    list_editable = ("published",)
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    autocomplete_fields = ("author",)
    readonly_fields = ("created_at", "updated_at", "cover_preview")
    date_hierarchy = "published_at"

    cover_preview = thumbnail("cover_image", height=50, label="Cover")

    def save_model(self, request, obj, form, change):  # noqa: ANN001
        # Default the author to the editing admin when unset.
        if obj.author_id is None:
            obj.author = request.user
        super().save_model(request, obj, form, change)
