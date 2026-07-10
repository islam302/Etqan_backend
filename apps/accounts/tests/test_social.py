"""Tests for social login (provider verification is mocked)."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from apps.accounts import views
from apps.accounts.models import SocialAccount
from apps.accounts.social import SocialUserData

User = get_user_model()

pytestmark = pytest.mark.django_db


def _fake(provider, uid, email, name):
    return lambda *a, **k: SocialUserData(provider, uid, email, name)


class TestGoogleLogin:
    def test_first_login_creates_user_and_links_account(self, api, monkeypatch):
        monkeypatch.setattr(
            views, "verify_google", _fake("google", "g-1", "g@user.com", "Gina")
        )
        resp = api.post("/api/auth/social/google/", {"id_token": "tok"}, format="json")
        assert resp.status_code == 200
        assert "access" in resp.data and "refresh" in resp.data
        assert resp.data["user"]["email"] == "g@user.com"

        user = User.objects.get(email="g@user.com")
        assert user.has_usable_password() is False
        assert user.username  # auto-generated
        assert SocialAccount.objects.filter(
            provider="google", uid="g-1", user=user
        ).exists()

    def test_repeat_login_reuses_same_user(self, api, monkeypatch):
        monkeypatch.setattr(
            views, "verify_google", _fake("google", "g-1", "g@user.com", "Gina")
        )
        api.post("/api/auth/social/google/", {"id_token": "t1"}, format="json")
        api.post("/api/auth/social/google/", {"id_token": "t2"}, format="json")
        assert User.objects.filter(email="g@user.com").count() == 1
        assert SocialAccount.objects.filter(provider="google", uid="g-1").count() == 1

    def test_links_to_existing_email_user(self, api, monkeypatch):
        existing = User.objects.create_user(
            email="dup@user.com", username="dup", password="pass12345"
        )
        monkeypatch.setattr(
            views, "verify_google", _fake("google", "g-9", "dup@user.com", "Dup")
        )
        resp = api.post("/api/auth/social/google/", {"id_token": "tok"}, format="json")
        assert resp.status_code == 200
        assert resp.data["user"]["id"] == str(existing.id)
        assert User.objects.filter(email="dup@user.com").count() == 1

    def test_missing_token_is_400(self, api):
        resp = api.post("/api/auth/social/google/", {}, format="json")
        assert resp.status_code == 400


class TestAppleAndFacebook:
    def test_apple_login(self, api, monkeypatch):
        monkeypatch.setattr(
            views,
            "verify_apple",
            lambda *a, **k: SocialUserData("apple", "a-1", "a@user.com", "Appler"),
        )
        resp = api.post(
            "/api/auth/social/apple/",
            {"identity_token": "tok", "name": "Appler"},
            format="json",
        )
        assert resp.status_code == 200
        assert SocialAccount.objects.filter(provider="apple", uid="a-1").exists()

    def test_facebook_login(self, api, monkeypatch):
        monkeypatch.setattr(
            views, "verify_facebook", _fake("facebook", "f-1", "f@user.com", "Facer")
        )
        resp = api.post(
            "/api/auth/social/facebook/", {"access_token": "tok"}, format="json"
        )
        assert resp.status_code == 200
        assert resp.data["user"]["email"] == "f@user.com"

    def test_apple_missing_token_is_400(self, api):
        assert api.post("/api/auth/social/apple/", {}, format="json").status_code == 400

    def test_facebook_missing_token_is_400(self, api):
        resp = api.post("/api/auth/social/facebook/", {}, format="json")
        assert resp.status_code == 400
