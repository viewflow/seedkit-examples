from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_health_check_ok(self):
        response = self.client.get(reverse("health-check"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


class IndexViewTests(TestCase):
    def test_index_ok(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)


class GdprViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pw")

    def test_data_export_requires_login(self):
        response = self.client.get(reverse("gdpr-data-export"))
        self.assertEqual(response.status_code, 302)

    def test_data_export(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("gdpr-data-export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "alice")

    def test_data_delete(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("gdpr-data-delete"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
