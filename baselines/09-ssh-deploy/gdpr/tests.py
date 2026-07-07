import io

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class GdprCommandsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="jane", email="jane@example.com", password="pw"
        )

    def test_export_user_data(self):
        out = io.StringIO()
        call_command("export_user_data", "jane", stdout=out)
        self.assertIn("jane@example.com", out.getvalue())

    def test_delete_user_data(self):
        call_command("delete_user_data", "jane@example.com", "--noinput")
        self.assertFalse(get_user_model().objects.filter(username="jane").exists())
