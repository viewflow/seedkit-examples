"""Send a test email (text + HTML alternative) to verify the outbound mail flow."""

from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone


class Command(BaseCommand):
    help = "Send a test email with text and HTML parts to the given recipient."

    def add_arguments(self, parser):
        parser.add_argument("recipient", help="Email address to send the test message to")
        parser.add_argument(
            "--subject",
            default="05-orbit-demo test email",
            help="Subject line (default: %(default)s)",
        )

    def handle(self, *args, **options):
        context = {
            "subject": options["subject"],
            "sent_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
        }
        message = EmailMultiAlternatives(
            subject=options["subject"],
            body=render_to_string("mailer/test_email.txt", context),
            to=[options["recipient"]],
        )
        message.attach_alternative(
            render_to_string("mailer/test_email.html", context), "text/html"
        )
        sent = message.send()
        self.stdout.write(
            self.style.SUCCESS(f"Sent {sent} message to {options['recipient']}")
        )
