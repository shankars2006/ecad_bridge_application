# blog/management/commands/create_initial_superuser.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Create initial superuser from env vars if it does not exist."

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv("SUPERUSER_USERNAME")
        email = os.getenv("SUPERUSER_EMAIL")
        password = os.getenv("SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(self.style.WARNING("SUPERUSER_USERNAME and SUPERUSER_PASSWORD must be set."))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists."))
            return

        User.objects.create_superuser(username=username, email=email or "", password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))