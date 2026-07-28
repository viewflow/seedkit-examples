import json

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.gdpr import export_user_data


class Command(BaseCommand):
    help = "Export all personal data held for a user as JSON (GDPR art. 15/20)."

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **options):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=options["username"])
        except user_model.DoesNotExist as exc:
            raise CommandError(f"User {options['username']!r} not found") from exc
        self.stdout.write(json.dumps(export_user_data(user), indent=2))
