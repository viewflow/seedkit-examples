from io import StringIO

from django.core import mail
from django.core.management import call_command
from django.test import TestCase


class SendTestEmailCommandTests(TestCase):
    def test_sends_html_and_text_email(self):
        call_command("send_test_email", "--to", "someone@example.com", stdout=StringIO())

        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ["someone@example.com"])
        self.assertTrue(any(mimetype == "text/html" for _, mimetype in sent.alternatives))
