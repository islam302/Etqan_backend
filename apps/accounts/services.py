"""Account services: JWT issuance, username generation, social user linking."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from rest_framework_simplejwt.tokens import RefreshToken

from .models import SocialAccount
from .social import SocialUserData

User = get_user_model()


def issue_tokens(user) -> dict:
    """Return an access/refresh pair (with a small user payload) for ``user``."""
    from .serializers import UserSerializer  # local import to avoid a cycle

    refresh = RefreshToken.for_user(user)
    refresh["email"] = user.email
    refresh["name"] = user.name
    refresh["username"] = user.username or ""
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": UserSerializer(user).data,
    }


def generate_unique_username(base: str) -> str:
    """Derive a unique username from ``base`` (email/name), suffixing on clash."""
    root = slugify((base or "user").split("@")[0]) or "user"
    root = root[:140]
    candidate = root
    while User.objects.filter(username=candidate).exists():
        candidate = f"{root}-{get_random_string(5).lower()}"
    return candidate


@transaction.atomic
def get_or_create_user_from_social(data: SocialUserData):
    """Resolve a local user for a verified social identity.

    Resolution order:
      1. Existing ``SocialAccount`` with the same ``(provider, uid)``.
      2. Existing user with the same email (links a new SocialAccount).
      3. Otherwise create a new user with an unusable password.
    """
    account = (
        SocialAccount.objects.select_related("user")
        .filter(provider=data.provider, uid=data.uid)
        .first()
    )
    if account:
        return account.user

    user = None
    if data.email:
        user = User.objects.filter(email__iexact=data.email).first()

    if user is None:
        email = data.email or f"{data.provider}_{data.uid}@users.noreply.etqan"
        user = User(
            email=email,
            name=data.name or "",
            username=generate_unique_username(data.email or data.name or data.provider),
        )
        user.set_unusable_password()
        user.save()

    SocialAccount.objects.create(
        user=user,
        provider=data.provider,
        uid=data.uid,
        extra_email=data.email or "",
    )
    return user
