"""Serializers for opinions."""

from __future__ import annotations

from rest_framework import serializers

from .models import Opinion


class OpinionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opinion
        fields = [
            "id",
            "quote",
            "author_name",
            "author_role",
            "avatar",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
