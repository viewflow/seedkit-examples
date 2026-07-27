from django.test import TestCase
from django.urls import reverse

from .models import Post


class PostModelTests(TestCase):
    def test_get_absolute_url(self):
        post = Post.objects.create(title="Hello", slug="hello", body="World")
        self.assertEqual(post.get_absolute_url(), f"/{post.slug}/")


class PostViewTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title="Hello", slug="hello", body="World")

    def test_post_list_view(self):
        response = self.client.get(reverse("post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_detail_view(self):
        response = self.client.get(reverse("post_detail", kwargs={"slug": self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.body)
