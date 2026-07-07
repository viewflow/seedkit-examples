from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class Command(BaseCommand):
    help = "Send a test email through the configured EMAIL_BACKEND."

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            default="test@example.com",
            help="Recipient address (default: test@example.com).",
        )

    def handle(self, *args, **options):
        to_address = options["to"]
        context = {"site_name": "05 Orbit Demo"}
        html_body = render_to_string("mailer/email/test_email.html", context)
        text_body = strip_tags(html_body)

        message = EmailMultiAlternatives(
            subject="Test email from 05 Orbit Demo",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_address],
        )
        message.attach_alternative(html_body, "text/html")
        message.send()

        self.stdout.write(
            self.style.SUCCESS(f"Sent test email to {to_address} via {settings.EMAIL_BACKEND}")
        )
