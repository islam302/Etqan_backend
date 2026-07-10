"""Populate the database with ETQAN demo content.

Idempotent: safe to run repeatedly. Uses ``get_or_create``/``update_or_create``
keyed on natural fields so re-running refreshes rather than duplicates data.

Usage::

    python manage.py seed_demo
    python manage.py seed_demo --admin-email me@etqan.agency --admin-password secret
"""

from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.blog.models import BlogPost, Tag
from apps.clients.models import Client
from apps.contact.models import ContactMessage
from apps.opinions.models import Opinion
from apps.pages.models import TeamMember
from apps.projects.models import Project, ProjectCategory
from apps.services.models import Service
from apps.settings.models import SiteSettings

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with ETQAN demo/placeholder content."

    def add_arguments(self, parser) -> None:  # noqa: ANN001
        parser.add_argument("--admin-email", default="admin@etqan.agency")
        parser.add_argument("--admin-password", default="Admin12345!")
        parser.add_argument(
            "--flush-content",
            action="store_true",
            help="Delete existing demo content before seeding.",
        )

    @transaction.atomic
    def handle(self, *args: Any, **options: Any) -> None:
        if options["flush_content"]:
            self._flush()

        admin = self._seed_admin(options["admin_email"], options["admin_password"])
        self._seed_services()
        self._seed_projects()
        self._seed_blog(admin)
        self._seed_opinions()
        self._seed_team()
        self._seed_clients()
        self._seed_messages()
        self._seed_settings()

        self.stdout.write(self.style.SUCCESS("\nETQAN demo data seeded."))
        self.stdout.write(
            f"  Admin login: {options['admin_email']} / {options['admin_password']}"
        )

    # ------------------------------------------------------------------ #
    def _flush(self) -> None:
        for model in (
            Project,
            Service,
            BlogPost,
            Tag,
            Opinion,
            TeamMember,
            Client,
            ContactMessage,
        ):
            model.objects.all().delete()
        self.stdout.write(self.style.WARNING("Flushed existing demo content."))

    def _seed_admin(self, email: str, password: str):
        admin, created = User.objects.get_or_create(
            email=email,
            defaults={"name": "ETQAN Admin", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password(password)
            admin.save()
            self.stdout.write(f"Created admin user: {email}")
        else:
            self.stdout.write(f"Admin user already exists: {email}")
        return admin

    def _seed_services(self) -> None:
        services = [
            {
                "title": "Web Development",
                "short_description": "Fast, scalable web apps built with modern stacks.",
                "long_description": (
                    "We design and build performant, SEO-friendly web applications "
                    "using React, Next.js and Django — from marketing sites to complex "
                    "dashboards."
                ),
                "icon": "code",
                "features": [
                    "Next.js & React",
                    "REST & GraphQL APIs",
                    "SEO optimized",
                    "CI/CD",
                ],
                "order": 1,
            },
            {
                "title": "Mobile Applications",
                "short_description": "Native-quality iOS & Android apps.",
                "long_description": (
                    "Cross-platform mobile apps with Flutter and React Native that feel "
                    "native and ship fast."
                ),
                "icon": "smartphone",
                "features": [
                    "iOS & Android",
                    "Offline-first",
                    "Push notifications",
                    "App Store launch",
                ],
                "order": 2,
            },
            {
                "title": "UI/UX Design",
                "short_description": "Human-centered product design that converts.",
                "long_description": (
                    "Research-driven interface and experience design, from wireframes "
                    "and prototypes to polished design systems."
                ),
                "icon": "palette",
                "features": [
                    "User research",
                    "Design systems",
                    "Prototyping",
                    "Usability testing",
                ],
                "order": 3,
            },
            {
                "title": "Software Solutions",
                "short_description": "Custom software & enterprise integrations.",
                "long_description": (
                    "Bespoke software, automation and enterprise integrations tailored "
                    "to your operations and scaled to your growth."
                ),
                "icon": "server",
                "features": [
                    "Custom platforms",
                    "Cloud & DevOps",
                    "Integrations",
                    "Automation",
                ],
                "order": 4,
            },
        ]
        for data in services:
            Service.objects.update_or_create(title=data["title"], defaults=data)
        self.stdout.write(f"Seeded {len(services)} services.")

    def _seed_projects(self) -> None:
        projects = [
            {
                "title": "Nimbus Analytics Platform",
                "category": ProjectCategory.WEB,
                "summary": "Real-time analytics dashboard for a fintech scale-up.",
                "tech_stack": ["Next.js", "Django", "PostgreSQL", "Redis"],
                "client_name": "Nimbus Finance",
                "is_featured": True,
                "order": 1,
            },
            {
                "title": "Zenith Fitness App",
                "category": ProjectCategory.MOBILE,
                "summary": "Cross-platform fitness tracking with wearable sync.",
                "tech_stack": ["Flutter", "Firebase", "GraphQL"],
                "client_name": "Zenith Health",
                "is_featured": True,
                "order": 2,
            },
            {
                "title": "Aurora Design System",
                "category": ProjectCategory.UIUX,
                "summary": "A unified design system for a multi-product SaaS suite.",
                "tech_stack": ["Figma", "Storybook", "React"],
                "client_name": "Aurora Cloud",
                "is_featured": False,
                "order": 3,
            },
            {
                "title": "Meridian ERP",
                "category": ProjectCategory.ENTERPRISE,
                "summary": "End-to-end ERP replacing legacy manufacturing systems.",
                "tech_stack": ["Django", "React", "Celery", "AWS"],
                "client_name": "Meridian Industries",
                "is_featured": True,
                "order": 4,
            },
            {
                "title": "Coral E-commerce",
                "category": ProjectCategory.WEB,
                "summary": "Headless storefront with a 40% faster checkout.",
                "tech_stack": ["Next.js", "Stripe", "Shopify"],
                "client_name": "Coral Retail",
                "is_featured": False,
                "order": 5,
            },
            {
                "title": "Pulse Delivery",
                "category": ProjectCategory.MOBILE,
                "summary": "Logistics app with live driver tracking and routing.",
                "tech_stack": ["React Native", "Node.js", "MapBox"],
                "client_name": "Pulse Logistics",
                "is_featured": False,
                "order": 6,
            },
        ]
        for data in projects:
            Project.objects.update_or_create(
                title=data["title"],
                defaults={**data, "description": data["summary"], "published": True},
            )
        self.stdout.write(f"Seeded {len(projects)} projects.")

    def _seed_blog(self, author) -> None:
        posts = [
            {
                "title": "Building the Future of Software",
                "excerpt": "How ETQAN approaches modern product engineering.",
                "tags": ["Engineering", "Culture"],
            },
            {
                "title": "Why We Bet on Next.js and Django",
                "excerpt": "Our default stack for shipping fast without technical debt.",
                "tags": ["Engineering", "Web"],
            },
            {
                "title": "Designing Products People Love",
                "excerpt": "The research-driven design process behind our work.",
                "tags": ["Design", "UX"],
            },
            {
                "title": "Scaling Mobile Apps to Millions",
                "excerpt": "Architecture lessons from high-traffic mobile products.",
                "tags": ["Mobile", "Architecture"],
            },
        ]
        for data in posts:
            tag_names = data.pop("tags")
            post, _ = BlogPost.objects.update_or_create(
                title=data["title"],
                defaults={
                    **data,
                    "body": (
                        f"# {data['title']}\n\n{data['excerpt']}\n\n"
                        "At ETQAN we believe great software is a blend of engineering "
                        "rigor and thoughtful design. This article explores our approach."
                    ),
                    "author": author,
                    "published": True,
                    "published_at": timezone.now(),
                    "meta_title": data["title"],
                    "meta_description": data["excerpt"],
                },
            )
            tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
            post.tags.set(tags)
        self.stdout.write(f"Seeded {len(posts)} blog posts.")

    def _seed_opinions(self) -> None:
        opinions = [
            {
                "quote": "ETQAN turned our vision into a product our customers love.",
                "author_name": "Sara Al-Mansour",
                "author_role": "CEO, Nimbus Finance",
                "order": 1,
            },
            {
                "quote": "The most reliable engineering partner we've worked with.",
                "author_name": "David Chen",
                "author_role": "CTO, Zenith Health",
                "order": 2,
            },
            {
                "quote": "Design and delivery were flawless from day one.",
                "author_name": "Layla Hassan",
                "author_role": "Head of Product, Aurora Cloud",
                "order": 3,
            },
        ]
        for data in opinions:
            Opinion.objects.update_or_create(
                author_name=data["author_name"], defaults=data
            )
        self.stdout.write(f"Seeded {len(opinions)} opinions.")

    def _seed_team(self) -> None:
        members = [
            {
                "name": "Omar Farouk",
                "role": "Founder & CEO",
                "bio": "15 years building software products across fintech and health.",
                "socials": {
                    "linkedin": "https://linkedin.com/in/omar",
                    "x": "https://x.com/omar",
                },
                "order": 1,
            },
            {
                "name": "Nadia Ibrahim",
                "role": "Head of Engineering",
                "bio": "Full-stack architect passionate about scalable systems.",
                "socials": {"github": "https://github.com/nadia"},
                "order": 2,
            },
            {
                "name": "Youssef Kamal",
                "role": "Lead Designer",
                "bio": "Crafting delightful, accessible product experiences.",
                "socials": {"dribbble": "https://dribbble.com/youssef"},
                "order": 3,
            },
        ]
        for data in members:
            TeamMember.objects.update_or_create(name=data["name"], defaults=data)
        self.stdout.write(f"Seeded {len(members)} team members.")

    def _seed_clients(self) -> None:
        clients = [
            "Nimbus Finance",
            "Zenith Health",
            "Aurora Cloud",
            "Meridian Industries",
            "Coral Retail",
            "Pulse Logistics",
        ]
        for i, name in enumerate(clients, start=1):
            Client.objects.update_or_create(
                name=name,
                defaults={"website": "https://example.com", "order": i},
            )
        self.stdout.write(f"Seeded {len(clients)} clients.")

    def _seed_messages(self) -> None:
        samples = [
            {
                "name": "Potential Client",
                "email": "lead@example.com",
                "subject": "New project inquiry",
                "message": "We'd love to discuss building a mobile app with your team.",
            },
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "subject": "Partnership",
                "message": "Interested in a long-term engineering partnership.",
                "is_read": True,
            },
        ]
        for data in samples:
            ContactMessage.objects.get_or_create(
                email=data["email"], subject=data["subject"], defaults=data
            )
        self.stdout.write(f"Seeded {len(samples)} contact messages.")

    def _seed_settings(self) -> None:
        settings_obj = SiteSettings.load()
        settings_obj.hero_title = "Building the Future of Software"
        settings_obj.hero_subtitle = (
            "ETQAN is a software agency crafting web, mobile and enterprise "
            "products that scale."
        )
        settings_obj.announcement_text = "We're hiring! Join the ETQAN team."
        settings_obj.company_about = (
            "ETQAN is a full-service software agency partnering with ambitious "
            "companies to design, build and scale digital products."
        )
        settings_obj.mission = (
            "To empower businesses with software that is fast, reliable and beautiful."
        )
        settings_obj.vision = (
            "To be the most trusted engineering partner in the region."
        )
        settings_obj.values = [
            {"title": "Craftsmanship", "description": "We sweat the details."},
            {"title": "Partnership", "description": "Your goals are our goals."},
            {"title": "Transparency", "description": "Clear, honest communication."},
        ]
        settings_obj.stats = {
            "projects": 120,
            "clients": 48,
            "retention": 96,
            "awards": 14,
        }
        settings_obj.contact_email = "hello@etqan.agency"
        settings_obj.contact_phone = "+20 100 000 0000"
        settings_obj.address = "Cairo, Egypt"
        settings_obj.social_links = {
            "linkedin": "https://linkedin.com/company/etqan",
            "x": "https://x.com/etqan",
            "github": "https://github.com/etqan",
            "instagram": "https://instagram.com/etqan",
        }
        settings_obj.save()
        self.stdout.write("Seeded site settings singleton.")
