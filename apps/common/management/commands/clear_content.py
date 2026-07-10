"""Delete all content records from every content API.

Removes the demo/placeholder data created by ``seed_demo`` (projects,
services, blog, opinions, team, clients, contact messages) and resets the
site-settings singleton to empty values.

By design it does NOT delete user accounts, so your admin login keeps working.
Pass ``--include-users`` to also remove non-superuser accounts.

Usage::

    python manage.py clear_content
    python manage.py clear_content --yes            # skip the confirmation prompt
    python manage.py clear_content --include-users  # also delete non-superusers
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.blog.models import BlogPost, Tag
from apps.clients.models import Client
from apps.contact.models import ContactMessage
from apps.opinions.models import Opinion
from apps.pages.models import TeamMember
from apps.projects.models import Project, ProjectImage
from apps.services.models import Service
from apps.settings.models import SiteSettings

User = get_user_model()

# Ordered so children are cleared before parents (ProjectImage before Project).
CONTENT_MODELS = (
    ProjectImage,
    Project,
    Service,
    BlogPost,
    Tag,
    Opinion,
    TeamMember,
    Client,
    ContactMessage,
)


class Command(BaseCommand):
    help = "Delete all content records (demo/placeholder data) from every API."

    def add_arguments(self, parser) -> None:  # noqa: ANN001
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip the interactive confirmation prompt.",
        )
        parser.add_argument(
            "--include-users",
            action="store_true",
            help="Also delete non-superuser accounts.",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        if not options["yes"]:
            confirm = input(
                "This deletes ALL content records (projects, services, blog, "
                "opinions, team, clients, messages) and resets site settings.\n"
                "Type 'yes' to continue: "
            )
            if confirm.strip().lower() != "yes":
                self.stdout.write(self.style.WARNING("Aborted. Nothing deleted."))
                return

        total = 0
        for model in CONTENT_MODELS:
            deleted, _ = model.objects.all().delete()
            total += deleted
            self.stdout.write(f"Cleared {model.__name__}: {deleted} row(s).")

        self._reset_settings()

        if options["include_users"]:
            deleted, _ = User.objects.filter(is_superuser=False).delete()
            self.stdout.write(f"Deleted {deleted} non-superuser account(s).")

        self.stdout.write(
            self.style.SUCCESS(f"\nDone. Removed {total} content record(s).")
        )

    def _reset_settings(self) -> None:
        """Blank out the singleton's marketing/contact content."""
        s = SiteSettings.load()
        s.hero_title = ""
        s.hero_subtitle = ""
        s.announcement_text = ""
        s.company_about = ""
        s.mission = ""
        s.vision = ""
        s.values = []
        s.stats = {}
        s.contact_email = ""
        s.contact_phone = ""
        s.address = ""
        s.social_links = {}
        s.save()
        self.stdout.write("Reset site settings singleton to empty values.")
