from django.core.management.base import BaseCommand
from blog.models import UserProfile


class Command(BaseCommand):
    help = "Populate the database with initial user profiles"

    def handle(self, *args, **kwargs):
        profiles = [
            {
                "username": "Kaushal Kumar",
                "designation": "ECAD Engineer @ Nokia",
            },
        ]

        for profile in profiles:
            UserProfile.objects.create(
                username=profile["username"],
                designation=profile["designation"],
            )

        self.stdout.write(
            self.style.SUCCESS("Successfully populated user profiles")
        )
