import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q


class Command(BaseCommand):
    help = "Export a user's personal data as JSON (GDPR data portability request)."

    def add_arguments(self, parser):
        parser.add_argument("username_or_email")

    def handle(self, *args, **options):
        User = get_user_model()
        identifier = options["username_or_email"]
        try:
            user = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist as exc:
            raise CommandError(f"No user found for '{identifier}'") from exc

        data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
            "is_active": user.is_active,
        }
        self.stdout.write(json.dumps(data, cls=DjangoJSONEncoder, indent=2))
