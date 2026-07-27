from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published_at__isnull=False, published_at__lte=timezone.now())


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    body = models.TextField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave empty to keep the post as a draft.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    @property
    def is_published(self) -> bool:
        return self.published_at is not None and self.published_at <= timezone.now()
