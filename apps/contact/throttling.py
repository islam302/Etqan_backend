"""Throttle for the public contact endpoint."""

from __future__ import annotations

from rest_framework.throttling import AnonRateThrottle


class ContactRateThrottle(AnonRateThrottle):
    """Limit anonymous contact submissions (rate from settings 'contact')."""

    scope = "contact"
