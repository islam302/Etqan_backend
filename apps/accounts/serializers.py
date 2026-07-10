"""Serializers for authentication, registration and the current-user profile."""

from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public representation of the authenticated user."""

    is_admin = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "name",
            "is_staff",
            "is_admin",
            "date_joined",
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Email + username + password registration."""

    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "email", "username", "name", "password"]
        read_only_fields = ["id"]

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_password(self, value: str) -> str:
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def create(self, validated_data: dict[str, Any]) -> Any:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Authenticate with password and either an email or a username.

    Accepts ``email``, ``username`` or a generic ``login`` field.
    """

    login = serializers.CharField(
        required=False,
        help_text="Email or username. (Or send 'email'/'username' explicitly.)",
    )
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        identifier = attrs.get("login") or attrs.get("email") or attrs.get("username")
        password = attrs.get("password")
        if not identifier:
            raise serializers.ValidationError("Provide 'email', 'username' or 'login'.")

        # Resolve the identifier to an email, since USERNAME_FIELD is email.
        email = identifier
        if "@" not in identifier:
            user = User.objects.filter(username__iexact=identifier).first()
            email = user.email if user else None

        user = (
            authenticate(
                request=self.context.get("request"), username=email, password=password
            )
            if email
            else None
        )
        if user is None:
            # 401 (not 400): the request was well-formed but auth failed.
            raise AuthenticationFailed(
                "No active account found with the given credentials."
            )
        attrs["user"] = user
        return attrs


class SocialLoginSerializer(serializers.Serializer):
    """Generic body for a social login token exchange."""

    id_token = serializers.CharField(required=False)
    identity_token = serializers.CharField(required=False)
    access_token = serializers.CharField(required=False)
    name = serializers.CharField(required=False, allow_blank=True)
