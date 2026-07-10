"""Contact submission (public) and message management (admin)."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from .models import ContactMessage
from .serializers import ContactMessageCreateSerializer, ContactMessageSerializer
from .throttling import ContactRateThrottle

logger = logging.getLogger(__name__)


class ContactSubmitView(CreateAPIView):
    """Public endpoint to submit a contact message.

    Always saves the message and emails a notification to the agency inbox
    (``CONTACT_NOTIFY_EMAIL``) via the configured email backend. Throttled per
    IP (see the ``contact`` throttle scope).
    """

    serializer_class = ContactMessageCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ContactRateThrottle]

    def perform_create(self, serializer: ContactMessageCreateSerializer) -> None:
        message: ContactMessage = serializer.save()
        self._notify(message)

    @staticmethod
    def _notify(message: ContactMessage) -> None:
        """Email the agency inbox about a new message.

        Best-effort: any failure is logged but never breaks the submission,
        so the message is always saved. ``Reply-To`` is set to the visitor so
        the team can reply to them directly from the notification.
        """
        recipient = getattr(settings, "CONTACT_NOTIFY_EMAIL", "")
        if not recipient:
            return
        try:
            email = EmailMultiAlternatives(
                subject=f"[ETQAN] New contact message: {message.subject or 'No subject'}",
                body=(
                    "You received a new message from the ETQAN website.\n\n"
                    f"Name:    {message.name}\n"
                    f"Email:   {message.email}\n"
                    f"Subject: {message.subject or '—'}\n"
                    f"Sent at: {message.created_at:%Y-%m-%d %H:%M UTC}\n\n"
                    f"Message:\n{message.message}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
                reply_to=[message.email],
            )
            email.send(fail_silently=True)
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to send contact notification email")


class ContactMessageViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Admin-only management of received contact messages."""

    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["is_read"]
    search_fields = ["name", "email", "subject", "message"]
    ordering_fields = ["created_at", "is_read"]
    ordering = ["-created_at"]

    @extend_schema(request=None, responses=ContactMessageSerializer)
    @action(detail=True, methods=["patch"], url_path="mark-read")
    def mark_read(self, request: Request, pk: str | None = None) -> Response:
        """Convenience action to flag a single message as read."""
        message = self.get_object()
        message.is_read = True
        message.save(update_fields=["is_read", "updated_at"])
        return Response(self.get_serializer(message).data, status=status.HTTP_200_OK)
