"""Serializer for the site settings singleton."""

from __future__ import annotations

from rest_framework import serializers

from .models import SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "hero_title",
            "hero_subtitle",
            "announcement_text",
            "company_about",
            "mission",
            "vision",
            "values",
            "stats",
            "contact_email",
            "contact_phone",
            "address",
            "social_links",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]

    def validate_values(self, value: object) -> list:
        if not isinstance(value, list):
            raise serializers.ValidationError("values must be a list.")
        return value

    def validate_stats(self, value: object) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError("stats must be an object/dict.")
        return value

    def validate_social_links(self, value: object) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError("social_links must be an object/dict.")
        return value
