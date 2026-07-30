from mailauth.contrib.user.apps import AuthConfig


class MailAuthUserConfig(AuthConfig):
    default_auto_field = "django.db.models.AutoField"
