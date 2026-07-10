"""Server-side verification of third-party (social) identity tokens.

Each ``verify_*`` function validates a provider-issued token and returns a
normalized :class:`SocialUserData`. They raise DRF exceptions on failure so
views surface clean 4xx responses:

* ``NotImplementedError``-style config gaps -> ``ValidationError`` (provider
  not configured on the server).
* Bad/expired tokens -> ``AuthenticationFailed``.

Network-dependent verification (Google certs, Apple JWKS, Facebook Graph) is
isolated here so it can be mocked in tests.
"""

from __future__ import annotations

from typing import NamedTuple

import jwt
import requests
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jwt import PyJWKClient
from rest_framework.exceptions import AuthenticationFailed, ValidationError

APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"
APPLE_ISSUER = "https://appleid.apple.com"
FACEBOOK_GRAPH = "https://graph.facebook.com"
_HTTP_TIMEOUT = 10


class SocialUserData(NamedTuple):
    """Normalized identity extracted from a verified provider token."""

    provider: str
    uid: str
    email: str
    name: str


def _cfg(key: str):
    return settings.SOCIAL_AUTH.get(key)


def verify_google(id_token_value: str) -> SocialUserData:
    """Verify a Google ID token and return the user's identity."""
    client_ids = _cfg("GOOGLE_CLIENT_IDS")
    if not client_ids:
        raise ValidationError("Google login is not configured on the server.")
    try:
        # audience=None verifies signature/issuer/expiry; we check aud below so
        # multiple client IDs (web + iOS + Android) are all accepted.
        claims = google_id_token.verify_oauth2_token(
            id_token_value, google_requests.Request()
        )
    except ValueError as exc:
        raise AuthenticationFailed("Invalid Google token.") from exc

    if claims.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise AuthenticationFailed("Invalid Google token issuer.")
    if claims.get("aud") not in client_ids:
        raise AuthenticationFailed("Google token was issued for another app.")

    return SocialUserData(
        provider="google",
        uid=claims["sub"],
        email=claims.get("email", ""),
        name=claims.get("name", ""),
    )


def verify_apple(identity_token: str, name: str = "") -> SocialUserData:
    """Verify an Apple identity token (Sign in with Apple) against Apple JWKS."""
    audiences = _cfg("APPLE_CLIENT_IDS")
    if not audiences:
        raise ValidationError("Apple login is not configured on the server.")
    try:
        signing_key = PyJWKClient(APPLE_KEYS_URL).get_signing_key_from_jwt(
            identity_token
        )
        claims = jwt.decode(
            identity_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audiences,
            issuer=APPLE_ISSUER,
        )
    except (jwt.PyJWTError, Exception) as exc:  # noqa: BLE001 - normalize to 401
        raise AuthenticationFailed("Invalid Apple token.") from exc

    return SocialUserData(
        provider="apple",
        uid=claims["sub"],
        email=claims.get("email", ""),
        name=name or "",
    )


def verify_facebook(access_token: str) -> SocialUserData:
    """Verify a Facebook access token belongs to our app and fetch the profile."""
    app_id = _cfg("FACEBOOK_APP_ID")
    app_secret = _cfg("FACEBOOK_APP_SECRET")
    if not app_id or not app_secret:
        raise ValidationError("Facebook login is not configured on the server.")

    app_token = f"{app_id}|{app_secret}"
    try:
        debug = requests.get(
            f"{FACEBOOK_GRAPH}/debug_token",
            params={"input_token": access_token, "access_token": app_token},
            timeout=_HTTP_TIMEOUT,
        ).json()
        data = debug.get("data", {})
        if not data.get("is_valid") or str(data.get("app_id")) != str(app_id):
            raise AuthenticationFailed("Invalid Facebook token.")

        profile = requests.get(
            f"{FACEBOOK_GRAPH}/me",
            params={"fields": "id,name,email", "access_token": access_token},
            timeout=_HTTP_TIMEOUT,
        ).json()
    except requests.RequestException as exc:
        raise AuthenticationFailed("Could not reach Facebook.") from exc

    if "id" not in profile:
        raise AuthenticationFailed("Invalid Facebook token.")

    return SocialUserData(
        provider="facebook",
        uid=profile["id"],
        email=profile.get("email", ""),
        name=profile.get("name", ""),
    )
