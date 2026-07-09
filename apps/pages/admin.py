"""Admin for team members."""

from __future__ import annotations

from django.contrib import admin

from apps.common.admin import thumbnail

from .models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "photo_preview", "role", "order", "is_active")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("name", "role", "bio")
    readonly_fields = ("created_at", "updated_at", "photo_preview")

    photo_preview = thumbnail("photo", label="Photo")
