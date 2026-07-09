"""Serializers for blog posts and tags."""

from __future__ import annotations

from rest_framework import serializers

from .models import BlogPost, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]


class AuthorSerializer(serializers.Serializer):
    """Minimal author payload embedded in blog responses."""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)


class BlogPostSerializer(serializers.ModelSerializer):
    """Read/write serializer for blog posts.

    Tags are read as nested objects and written by slug list via
    ``tag_slugs``.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    tag_slugs = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of tag names; created on the fly if missing.",
    )

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "cover_image",
            "excerpt",
            "body",
            "tags",
            "tag_slugs",
            "author",
            "published",
            "published_at",
            "meta_title",
            "meta_description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "author",
            "published_at",
            "created_at",
            "updated_at",
        ]

    def _resolve_tags(self, names: list[str]) -> list[Tag]:
        tags: list[Tag] = []
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name.strip())
            tags.append(tag)
        return tags

    def create(self, validated_data: dict) -> BlogPost:
        tag_names = validated_data.pop("tag_slugs", None)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("author", request.user)
        post = super().create(validated_data)
        if tag_names is not None:
            post.tags.set(self._resolve_tags(tag_names))
        return post

    def update(self, instance: BlogPost, validated_data: dict) -> BlogPost:
        tag_names = validated_data.pop("tag_slugs", None)
        post = super().update(instance, validated_data)
        if tag_names is not None:
            post.tags.set(self._resolve_tags(tag_names))
        return post
