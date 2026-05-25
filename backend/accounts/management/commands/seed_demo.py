import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Organization
from ingestion.models import DataSourceConfig

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo organization, analyst user, and default data source configs."

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            slug="demo-corp",
            defaults={"name": "Demo Corporation"},
        )

        email = os.environ.get("DEMO_ANALYST_EMAIL", "analyst@demo.breathe.local")
        password = os.environ.get("DEMO_ANALYST_PASSWORD", "demo-analyst-2025")

        user = User.objects.filter(username=email).first()
        if user is None:
            User.objects.create_user(
                username=email,
                email=email,
                password=password,
                organization=org,
                role=User.Role.ANALYST,
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS(f"Created analyst: {email}"))
        else:
            user.set_password(password)
            user.save(update_fields=["password"])
            self.stdout.write(f"Reset password for existing analyst: {email}")

        plant_lookup = {
            "1000": {"site_name": "Berlin Plant", "country": "DE"},
            "DE01": {"site_name": "Munich Office", "country": "DE"},
        }
        for source in ("SAP", "UTILITY", "TRAVEL"):
            DataSourceConfig.objects.get_or_create(
                organization=org,
                source=source,
                defaults={"plant_lookup": plant_lookup if source == "SAP" else {}},
            )

        self.stdout.write(self.style.SUCCESS("Demo seed complete."))
