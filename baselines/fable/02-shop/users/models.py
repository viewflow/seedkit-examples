from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Project user model. Extend with profile fields as the shop grows."""
