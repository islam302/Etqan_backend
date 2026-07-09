"""Admin for contact messages (read-only content + bulk actions)."""

from __future__ import annotations

from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = (
        "name",
        "email",
        "subject",
        "message",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "created_at"
    actions = ("mark_read", "mark_unread")

    def has_add_permission(self, request) -> bool:  # noqa: ANN001
        # Messages are only created through the public API.
        return False

    @admin.action(description="Mark selected messages as read")
    def mark_read(self, request, queryset) -> None:  # noqa: ANN001
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} message(s) marked as read.")

    @admin.action(description="Mark selected messages as unread")
    def mark_unread(self, request, queryset) -> None:  # noqa: ANN001
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} message(s) marked as unread.")
