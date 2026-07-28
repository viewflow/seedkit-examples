"""A custom user model keyed by e-mail address."""

from typing import Any, ClassVar

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager["User"]):
    """Manager for a user model that has no username field."""

    def _create(self, email: str, password: str | None, **extra_fields: Any) -> "User":
        if not email:
            raise ValueError("Users must have an e-mail address.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(  # type: ignore[override]
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create(email, password, **extra_fields)

    def create_superuser(  # type: ignore[override]
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create(email, password, **extra_fields)


class User(AbstractUser):
    """Site user. Authentication is by e-mail; there is no username."""

    username = None  # type: ignore[assignment]
    email = models.EmailField("e-mail address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects: ClassVar[UserManager] = UserManager()  # type: ignore[assignment,misc]

    def __str__(self) -> str:
        return self.email
