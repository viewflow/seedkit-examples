from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model, kept close to Django's default for now."""
