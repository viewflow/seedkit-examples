from django.test import TestCase
from django.urls import reverse

from .models import Post


class PostViewTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(
            title='Hello World',
            slug='hello-world',
            body='My first post.',
        )

    def test_post_list(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_detail(self):
        response = self.client.get(reverse('blog:post_detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.body)
