from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.gdpr import delete_user_data


class Command(BaseCommand):
    help = "Anonymise a user's personal data (GDPR art. 17 right to erasure)."

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip the confirmation prompt.",
        )

    def handle(self, *args, **options):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=options["username"])
        except user_model.DoesNotExist as exc:
            raise CommandError(f"User {options['username']!r} not found") from exc

        if not options["yes"]:
            answer = input(f"Anonymise user {user.username!r}? [y/N] ")
            if answer.lower() != "y":
                self.stdout.write("Aborted.")
                return

        delete_user_data(user)
        self.stdout.write(self.style.SUCCESS(f"User {options['username']!r} anonymised."))
