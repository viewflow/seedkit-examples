from django.test import Client, TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_healthz(self):
        response = Client().get(reverse("healthz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_readyz(self):
        response = Client().get(reverse("readyz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
