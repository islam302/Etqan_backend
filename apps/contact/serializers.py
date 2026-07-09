"""Serializers for contact messages."""

from __future__ import annotations

from rest_framework import serializers

from .models import ContactMessage


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """Public submission serializer (write-only fields)."""

    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "subject", "message", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_message(self, value: str) -> str:
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Please provide a message of at least 10 characters."
            )
        return value


class ContactMessageSerializer(serializers.ModelSerializer):
    """Admin serializer for listing and updating (mark read) messages."""

    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "name",
            "email",
            "subject",
            "message",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "name",
            "email",
            "subject",
            "message",
            "created_at",
            "updated_at",
        ]
