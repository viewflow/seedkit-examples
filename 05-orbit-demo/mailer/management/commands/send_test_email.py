from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("recipient")

    def handle(self, *args, recipient, **opts):
        msg = EmailMultiAlternatives(
            subject="Test email",
            body="If you can read this, plain-text email delivery works.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        msg.attach_alternative(render_to_string("email/test.html"), "text/html")
        msg.send()
        self.stdout.write(self.style.SUCCESS(f"sent to {recipient}"))
