"""Production settings."""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# HTTPS enforcement. Enabled by default for real deployments (which sit behind
# a TLS-terminating proxy). Set SECURE_SSL_REDIRECT=False when running the prod
# image locally over plain HTTP (e.g. docker-compose), otherwise every request
# is 301-redirected to https:// and secure-only cookies break admin login.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=SECURE_SSL_REDIRECT)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=SECURE_SSL_REDIRECT)

# Security hardening (assumes TLS termination in front of the app).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365 if SECURE_SSL_REDIRECT else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# CSRF trusted origins should mirror the allowed frontend origins.
CSRF_TRUSTED_ORIGINS = [
    origin for origin in CORS_ALLOWED_ORIGINS if origin.startswith("http")  # noqa: F405
]
