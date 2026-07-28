from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SendTestEmailCommandTests(TestCase):
    def test_sends_text_and_html_parts(self):
        call_command("send_test_email", "to@example.com")

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["to@example.com"])
        self.assertIn("Test email", message.body)
        content, mimetype = message.alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn("<html", content)


class HealthCheckTests(TestCase):
    def test_healthz(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")

    def test_readyz(self):
        response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ready")
