from django.contrib.auth.models import User
from django.test import TestCase

from .models import Post


class PostModelTests(TestCase):
    def test_str_returns_title(self):
        post = Post.objects.create(title="Hello", slug="hello")
        self.assertEqual(str(post), "Hello")


class AdminSmokeTests(TestCase):
    def test_admin_login_page_renders(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_reach_admin_index(self):
        User.objects.create_superuser("admin", "admin@example.com", "s3cret-pass")
        self.client.login(username="admin", password="s3cret-pass")
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
