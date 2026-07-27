from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Post


class PostModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="author", password="pw"
        )

    def test_str_is_title(self):
        post = Post(title="Hello", slug="hello", author=self.author)
        self.assertEqual(str(post), "Hello")

    def test_published_queryset_excludes_drafts_and_future(self):
        Post.objects.create(title="Draft", slug="draft", author=self.author)
        Post.objects.create(
            title="Future",
            slug="future",
            author=self.author,
            published_at=timezone.now() + timedelta(days=1),
        )
        live = Post.objects.create(
            title="Live",
            slug="live",
            author=self.author,
            published_at=timezone.now(),
        )
        self.assertQuerySetEqual(Post.objects.published(), [live])


class PostViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username="author", password="pw"
        )
        cls.post = Post.objects.create(
            title="Live post",
            slug="live-post",
            body="Body text.",
            author=cls.author,
            published_at=timezone.now(),
        )
        cls.draft = Post.objects.create(
            title="Draft post", slug="draft-post", author=cls.author
        )

    def test_list_shows_published_only(self):
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Live post")
        self.assertNotContains(response, "Draft post")

    def test_detail_renders(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Body text.")

    def test_draft_detail_is_404(self):
        response = self.client.get(
            reverse("blog:post_detail", kwargs={"slug": self.draft.slug})
        )
        self.assertEqual(response.status_code, 404)


class AdminAccessTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_reach_admin_index(self):
        get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password="admin-pass-123"
        )
        self.assertTrue(self.client.login(username="admin", password="admin-pass-123"))
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)


class EmailBackendTests(TestCase):
    def test_console_backend_captured_by_test_runner(self):
        mail.send_mail("Subject", "Body", None, ["someone@example.com"])
        self.assertEqual(len(mail.outbox), 1)
