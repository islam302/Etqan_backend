"""Admin for clients."""

from __future__ import annotations

from django.contrib import admin

from apps.common.admin import thumbnail

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "logo_preview", "website", "order", "is_active")
    list_filter = ("is_active",)
    list_editable = ("order", "is_active")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at", "logo_preview")

    logo_preview = thumbnail("logo", label="Logo")
