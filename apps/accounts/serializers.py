"""Serializers for authentication and the current-user profile."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public representation of the authenticated admin user."""

    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "name", "is_staff", "is_admin", "date_joined"]
        read_only_fields = fields


class LoginSerializer(TokenObtainPairSerializer):
    """JWT login that also embeds a small user payload in the response."""

    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):  # type: ignore[override]
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.name
        return token

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
