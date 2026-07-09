"""Development settings."""

from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Be permissive with CORS locally so the frontend dev server just works.
CORS_ALLOW_ALL_ORIGINS = True

# Print emails to the console during development unless SMTP is configured.
if not env("EMAIL_HOST", default=""):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
