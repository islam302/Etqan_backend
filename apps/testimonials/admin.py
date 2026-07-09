"""Admin for testimonials."""

from __future__ import annotations

from django.contrib import admin

from apps.common.admin import thumbnail

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        "author_name",
        "avatar_preview",
        "author_role",
        "order",
        "is_active",
    )
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("author_name", "author_role", "quote")
    readonly_fields = ("created_at", "updated_at", "avatar_preview")

    avatar_preview = thumbnail("avatar", label="Avatar")
