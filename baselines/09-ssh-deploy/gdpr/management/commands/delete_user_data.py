from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q


class Command(BaseCommand):
    help = "Delete a user's account and personal data (GDPR right to erasure)."

    def add_arguments(self, parser):
        parser.add_argument("username_or_email")
        parser.add_argument(
            "--noinput",
            action="store_false",
            dest="interactive",
            help="Delete without asking for confirmation.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        identifier = options["username_or_email"]
        try:
            user = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist as exc:
            raise CommandError(f"No user found for '{identifier}'") from exc

        if options["interactive"]:
            confirm = input(f"Delete all data for user '{user.username}'? [y/N] ")
            if confirm.lower() != "y":
                self.stdout.write("Aborted.")
                return

        user.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted user '{identifier}'."))
