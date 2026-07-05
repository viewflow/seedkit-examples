from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    """GDPR right-to-erasure helper: delete a user and cascade to owned rows."""

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, user_id, **opts):
        with transaction.atomic():
            get_user_model().objects.filter(pk=user_id).delete()
        self.stdout.write(self.style.SUCCESS(f"deleted user {user_id}"))
