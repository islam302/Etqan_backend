"""Serializers for team members."""

from __future__ import annotations

from rest_framework import serializers

from .models import TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = [
            "id",
            "name",
            "role",
            "photo",
            "bio",
            "socials",
            "order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_socials(self, value: object) -> dict:
        if not isinstance(value, dict):
            raise serializers.ValidationError("socials must be an object/dict.")
        return value
