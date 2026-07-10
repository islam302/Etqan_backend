"""Authentication views: register, login, logout, me, and social login."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    SocialLoginSerializer,
    UserSerializer,
)
from .services import get_or_create_user_from_social, issue_tokens
from .social import verify_apple, verify_facebook, verify_google


class RegisterView(APIView):
    """Create a new account (email + username + password) and return JWTs."""

    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(issue_tokens(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Obtain a JWT pair using email OR username plus password."""

    permission_classes = [AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: UserSerializer})
    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(issue_tokens(serializer.validated_data["user"]))


class LogoutView(APIView):
    """Blacklist a refresh token so it can no longer be used."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"refresh": {"type": "string"}},
                "required": ["refresh"],
            }
        },
        responses={205: None, 400: None},
    )
    def post(self, request: Request) -> Response:
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "A 'refresh' token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(APIView):
    """Return the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses=UserSerializer)
    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)


class _SocialLoginView(APIView):
    """Base for provider token-exchange endpoints.

    Subclasses implement :meth:`verify` to turn the request into normalized
    social user data; the base handles user lookup/creation and token issuance.
    First-time logins create the account (registration == login for social).
    """

    permission_classes = [AllowAny]
    serializer_class = SocialLoginSerializer

    def verify(self, data: dict):  # pragma: no cover - overridden
        raise NotImplementedError

    @extend_schema(request=SocialLoginSerializer, responses={200: UserSerializer})
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        social_data = self.verify(serializer.validated_data)
        user = get_or_create_user_from_social(social_data)
        return Response(issue_tokens(user))


class GoogleLoginView(_SocialLoginView):
    """Exchange a Google ID token (`id_token`) for a JWT pair."""

    def verify(self, data: dict):
        token = data.get("id_token") or data.get("access_token")
        if not token:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"id_token": "This field is required."})
        return verify_google(token)


class AppleLoginView(_SocialLoginView):
    """Exchange an Apple identity token (`identity_token`) for a JWT pair."""

    def verify(self, data: dict):
        token = data.get("identity_token") or data.get("id_token")
        if not token:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"identity_token": "This field is required."})
        return verify_apple(token, name=data.get("name", ""))


class FacebookLoginView(_SocialLoginView):
    """Exchange a Facebook access token (`access_token`) for a JWT pair."""

    def verify(self, data: dict):
        token = data.get("access_token")
        if not token:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"access_token": "This field is required."})
        return verify_facebook(token)
