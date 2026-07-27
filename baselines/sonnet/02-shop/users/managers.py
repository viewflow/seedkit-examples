from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    """Default Django user manager, kept as an explicit hook for the custom User model."""
