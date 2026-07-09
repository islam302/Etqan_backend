"""Shared pytest fixtures for the ETQAN test suite."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture(autouse=True)
def _clear_throttle_cache():
    """Reset DRF throttle counters (cache-backed) between tests."""
    from django.core.cache import cache

    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api() -> APIClient:
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@etqan.test", password="pass12345", name="Admin"
    )


@pytest.fixture
def normal_user(db):
    return User.objects.create_user(
        email="user@etqan.test", password="pass12345", name="User"
    )


@pytest.fixture
def auth_admin(api: APIClient, admin_user) -> APIClient:
    """An APIClient authenticated as a staff/admin user via JWT."""
    resp = api.post(
        "/api/auth/login/",
        {"email": admin_user.email, "password": "pass12345"},
        format="json",
    )
    token = resp.data["access"]
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api
