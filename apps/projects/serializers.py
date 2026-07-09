"""Serializers for projects and nested gallery images."""

from __future__ import annotations

from rest_framework import serializers

from .models import Project, ProjectImage


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ["id", "image", "caption", "order"]


class ProjectSerializer(serializers.ModelSerializer):
    """Full project representation including its nested gallery."""

    gallery = ProjectImageSerializer(many=True, read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "category_display",
            "summary",
            "description",
            "cover_image",
            "gallery",
            "tech_stack",
            "client_name",
            "live_url",
            "is_featured",
            "published",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def validate_tech_stack(self, value: object) -> list:
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise serializers.ValidationError("tech_stack must be a list of strings.")
        return value
