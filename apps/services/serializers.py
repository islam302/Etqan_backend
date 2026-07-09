"""Serializers for the Service model."""

from __future__ import annotations

from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "long_description",
            "icon",
            "features",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def validate_features(self, value: object) -> list:
        if not isinstance(value, list):
            raise serializers.ValidationError("features must be a list of strings.")
        if not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError("Each feature must be a string.")
        return value
