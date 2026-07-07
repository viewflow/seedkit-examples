from django.test import TestCase

from users.models import User


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            username="alice", email="alice@example.com", password="s3cret-pass"
        )

        self.assertEqual(user.email, "alice@example.com")
        self.assertTrue(user.check_password("s3cret-pass"))
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="s3cret-pass"
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
