"""Tests for the blog model and API."""

from __future__ import annotations

import pytest

from apps.blog.models import BlogPost, Tag

pytestmark = pytest.mark.django_db


def _post(title="Post", published=True, **kw):
    return BlogPost.objects.create(title=title, body="body", published=published, **kw)


class TestBlogModel:
    def test_slug_and_publish_stamp(self):
        p = _post(title="Hello World")
        assert p.slug == "hello-world"
        assert p.published_at is not None

    def test_draft_has_no_publish_stamp(self):
        p = _post(title="Draft", published=False)
        assert p.published_at is None


class TestBlogAPI:
    def test_public_lists_only_published(self, api):
        _post(title="Live", published=True)
        _post(title="Draft", published=False)
        resp = api.get("/api/blog/")
        titles = [p["title"] for p in resp.data["results"]]
        assert "Live" in titles and "Draft" not in titles

    def test_filter_by_tag(self, api):
        p = _post(title="Tagged")
        tag = Tag.objects.create(name="Django")
        p.tags.add(tag)
        _post(title="Untagged")
        resp = api.get(f"/api/blog/?tag={tag.slug}")
        assert [x["title"] for x in resp.data["results"]] == ["Tagged"]

    def test_admin_create_with_tags_sets_author(self, auth_admin, admin_user):
        resp = auth_admin.post(
            "/api/blog/",
            {
                "title": "New",
                "body": "x",
                "published": True,
                "tag_slugs": ["AI", "Web"],
            },
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["author"]["email"] == admin_user.email
        assert {t["name"] for t in resp.data["tags"]} == {"AI", "Web"}

    def test_retrieve_by_slug(self, api):
        _post(title="Findable")
        resp = api.get("/api/blog/findable/")
        assert resp.status_code == 200
        assert resp.data["title"] == "Findable"
