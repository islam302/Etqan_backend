"""Admin for the site settings singleton."""

from __future__ import annotations

from django.contrib import admin
from django.http import HttpRequest

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Hero", {"fields": ("hero_title", "hero_subtitle", "announcement_text")}),
        (
            "About",
            {"fields": ("company_about", "mission", "vision", "values", "stats")},
        ),
        (
            "Contact",
            {"fields": ("contact_email", "contact_phone", "address", "social_links")},
        ),
        ("Meta", {"fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Only allow creating the singleton if it does not yet exist.
        return not SiteSettings.objects.exists()

    def has_delete_permission(
        self, request: HttpRequest, obj=None
    ) -> bool:  # noqa: ANN001
        return False
