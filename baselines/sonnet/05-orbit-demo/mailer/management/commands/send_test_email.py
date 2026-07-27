from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = "Send a test email (text + HTML alternative) to confirm outbound mail delivery."

    def add_arguments(self, parser):
        parser.add_argument("to", help="Recipient email address")

    def handle(self, *args, **options):
        recipient = options["to"]
        subject = "orbit-demo test email"
        context = {"subject": subject}

        text_body = render_to_string("emails/test_email.txt", context)
        html_body = render_to_string("emails/test_email.html", context)

        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        message.attach_alternative(html_body, "text/html")
        message.send()

        self.stdout.write(self.style.SUCCESS(f"Sent test email to {recipient}"))
