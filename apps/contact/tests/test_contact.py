"""Tests for contact submission and admin management."""

from __future__ import annotations

import pytest

from apps.contact.models import ContactMessage

pytestmark = pytest.mark.django_db

VALID = {
    "name": "Jane",
    "email": "jane@example.com",
    "subject": "Hi",
    "message": "I would like to build an app with you.",
}


class TestContactSubmit:
    def test_public_can_submit(self, api):
        resp = api.post("/api/contact/", VALID, format="json")
        assert resp.status_code == 201
        assert ContactMessage.objects.filter(email="jane@example.com").exists()

    def test_submit_emails_agency_inbox(self, api, settings, mailoutbox):
        settings.CONTACT_NOTIFY_EMAIL = "etqan.agency.company@gmail.com"
        resp = api.post("/api/contact/", VALID, format="json")
        assert resp.status_code == 201
        assert len(mailoutbox) == 1
        sent = mailoutbox[0]
        assert sent.to == ["etqan.agency.company@gmail.com"]
        # Reply-To is the visitor so the team can reply directly.
        assert sent.reply_to == ["jane@example.com"]
        assert "Jane" in sent.body and "build an app" in sent.body

    def test_short_message_rejected(self, api):
        resp = api.post("/api/contact/", {**VALID, "message": "hi"}, format="json")
        assert resp.status_code == 400

    def test_missing_email_rejected(self, api):
        payload = {k: v for k, v in VALID.items() if k != "email"}
        assert api.post("/api/contact/", payload, format="json").status_code == 400


class TestMessageAdmin:
    def test_list_requires_admin(self, api):
        assert api.get("/api/messages/").status_code in (401, 403)

    def test_admin_can_list_and_mark_read(self, auth_admin):
        msg = ContactMessage.objects.create(**VALID)
        assert msg.is_read is False

        listing = auth_admin.get("/api/messages/")
        assert listing.status_code == 200
        assert listing.data["count"] == 1

        marked = auth_admin.patch(f"/api/messages/{msg.id}/mark-read/")
        assert marked.status_code == 200
        msg.refresh_from_db()
        assert msg.is_read is True

    def test_filter_unread(self, auth_admin):
        ContactMessage.objects.create(**VALID, is_read=True)
        ContactMessage.objects.create(**{**VALID, "email": "b@x.com"}, is_read=False)
        resp = auth_admin.get("/api/messages/?is_read=false")
        assert resp.data["count"] == 1
