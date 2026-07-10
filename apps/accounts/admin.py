"""Admin configuration for the custom user model and social accounts."""

from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import SocialAccount, User


class UserCreationFormEmail(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "username", "name")


class UserChangeFormEmail(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class SocialAccountInline(admin.TabularInline):
    model = SocialAccount
    extra = 0
    fields = ("provider", "uid", "extra_email", "created_at")
    readonly_fields = ("provider", "uid", "extra_email", "created_at")
    can_delete = True

    def has_add_permission(self, request, obj=None) -> bool:  # noqa: ANN001
        return False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationFormEmail
    form = UserChangeFormEmail
    model = User

    list_display = (
        "email",
        "username",
        "name",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "username", "name")
    ordering = ("email",)
    readonly_fields = ("date_joined", "last_login")
    inlines = [SocialAccountInline]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username", "name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ("provider", "uid", "user", "extra_email", "created_at")
    list_filter = ("provider",)
    search_fields = ("uid", "extra_email", "user__email", "user__username")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)
