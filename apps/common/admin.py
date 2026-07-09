"""Small admin helpers shared across apps."""

from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html


def thumbnail(field_name: str, *, height: int = 40, label: str = "Preview"):
    """Return an admin display method rendering an ``<img>`` for ``field_name``.

    Usage inside a ``ModelAdmin``::

        preview = thumbnail("cover_image")
        list_display = ("title", "preview")
    """

    @admin.display(description=label)
    def _thumb(self, obj):  # noqa: ANN001
        image = getattr(obj, field_name, None)
        if image and hasattr(image, "url"):
            return format_html(
                '<img src="{}" style="height:{}px;border-radius:4px;" />',
                image.url,
                height,
            )
        return "—"

    return _thumb
