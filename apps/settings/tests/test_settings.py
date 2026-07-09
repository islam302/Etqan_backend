"""Tests for the site settings singleton and its endpoint."""

from __future__ import annotations

import pytest

from apps.settings.models import SiteSettings

pytestmark = pytest.mark.django_db


class TestSingleton:
    def test_load_creates_single_row(self):
        a = SiteSettings.load()
        b = SiteSettings.load()
        assert a.pk == b.pk == SiteSettings.SINGLETON_ID
        assert SiteSettings.objects.count() == 1

    def test_pk_pinned_on_save(self):
        s = SiteSettings(hero_title="X")
        s.save()
        assert s.pk == SiteSettings.SINGLETON_ID


class TestSettingsAPI:
    def test_public_get(self, api):
        resp = api.get("/api/settings/")
        assert resp.status_code == 200
        assert "hero_title" in resp.data

    def test_public_cannot_update(self, api):
        resp = api.patch("/api/settings/", {"hero_title": "Hacked"}, format="json")
        assert resp.status_code in (401, 403)

    def test_admin_can_update(self, auth_admin):
        resp = auth_admin.patch(
            "/api/settings/", {"hero_title": "Updated Hero"}, format="json"
        )
        assert resp.status_code == 200
        assert resp.data["hero_title"] == "Updated Hero"
        assert SiteSettings.load().hero_title == "Updated Hero"
