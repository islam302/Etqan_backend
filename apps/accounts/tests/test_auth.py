"""Tests for the custom user model and JWT auth flow."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestUserModel:
    def test_create_user_with_email(self):
        user = User.objects.create_user(email="a@b.com", password="x12345678")
        assert user.email == "a@b.com"
        assert user.check_password("x12345678")
        assert not user.is_staff
        assert user.is_admin is False

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="root@b.com", password="x12345678")
        assert admin.is_staff and admin.is_superuser
        assert admin.is_admin is True

    def test_email_required(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", password="x")


class TestAuthEndpoints:
    def test_login_returns_tokens_and_user(self, api, admin_user):
        resp = api.post(
            "/api/auth/login/",
            {"email": admin_user.email, "password": "pass12345"},
            format="json",
        )
        assert resp.status_code == 200
        assert "access" in resp.data and "refresh" in resp.data
        assert resp.data["user"]["email"] == admin_user.email

    def test_login_bad_credentials(self, api, admin_user):
        resp = api.post(
            "/api/auth/login/",
            {"email": admin_user.email, "password": "wrong"},
            format="json",
        )
        assert resp.status_code == 401

    def test_me_requires_auth(self, api):
        assert api.get("/api/auth/me/").status_code == 401

    def test_me_returns_profile(self, auth_admin, admin_user):
        resp = auth_admin.get("/api/auth/me/")
        assert resp.status_code == 200
        assert resp.data["email"] == admin_user.email

    def test_refresh_and_logout(self, api, admin_user):
        login = api.post(
            "/api/auth/login/",
            {"email": admin_user.email, "password": "pass12345"},
            format="json",
        )
        refresh = login.data["refresh"]

        refreshed = api.post("/api/auth/refresh/", {"refresh": refresh}, format="json")
        assert refreshed.status_code == 200
        assert "access" in refreshed.data

        # Authenticate then blacklist the (rotated) refresh token.
        api.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        new_refresh = refreshed.data.get("refresh", refresh)
        logout = api.post("/api/auth/logout/", {"refresh": new_refresh}, format="json")
        assert logout.status_code == 205


class TestRegistration:
    payload = {
        "email": "new@user.com",
        "username": "newbie",
        "name": "New User",
        "password": "Str0ngPass!23",
    }

    def test_register_creates_user_and_returns_tokens(self, api):
        resp = api.post("/api/auth/register/", self.payload, format="json")
        assert resp.status_code == 201
        assert "access" in resp.data and "refresh" in resp.data
        assert resp.data["user"]["username"] == "newbie"
        user = User.objects.get(email="new@user.com")
        assert user.check_password("Str0ngPass!23")

    def test_duplicate_email_rejected(self, api):
        api.post("/api/auth/register/", self.payload, format="json")
        resp = api.post("/api/auth/register/", self.payload, format="json")
        assert resp.status_code == 400
        assert "email" in resp.data

    def test_weak_password_rejected(self, api):
        resp = api.post(
            "/api/auth/register/",
            {**self.payload, "password": "123"},
            format="json",
        )
        assert resp.status_code == 400
        assert "password" in resp.data


class TestUsernameLogin:
    def test_login_with_username(self, api):
        User.objects.create_user(
            email="handle@user.com", username="cooldev", password="pass12345"
        )
        resp = api.post(
            "/api/auth/login/",
            {"username": "cooldev", "password": "pass12345"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["user"]["username"] == "cooldev"

    def test_login_with_generic_login_field(self, api):
        User.objects.create_user(
            email="handle2@user.com", username="devtwo", password="pass12345"
        )
        resp = api.post(
            "/api/auth/login/",
            {"login": "devtwo", "password": "pass12345"},
            format="json",
        )
        assert resp.status_code == 200
