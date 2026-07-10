"""Auth URL patterns mounted under /api/auth/."""

from __future__ import annotations

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AppleLoginView,
    FacebookLoginView,
    GoogleLoginView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
    # Social login / registration (token exchange)
    path("social/google/", GoogleLoginView.as_view(), name="social-google"),
    path("social/apple/", AppleLoginView.as_view(), name="social-apple"),
    path("social/facebook/", FacebookLoginView.as_view(), name="social-facebook"),
]
