from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager


class User(AbstractUser):
    """Custom user model, identified by email instead of username."""

    username = None
    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()  # pyright: ignore[reportIncompatibleVariableOverride]

    def __str__(self):
        return self.email
