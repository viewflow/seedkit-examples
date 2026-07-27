from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

User = get_user_model()


class _UniqueEmailMixin:
    def clean_email(self):
        email = self.cleaned_data["email"]
        if (
            email
            and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
        ):
            raise ValidationError("A user with that email already exists.")
        return email


class UniqueEmailUserCreationForm(_UniqueEmailMixin, UserCreationForm):
    pass


class UniqueEmailUserChangeForm(_UniqueEmailMixin, UserChangeForm):
    pass


class MailAuthUserAdmin(UserAdmin):
    """
    Enforces the same email uniqueness the auth_user_email_unique_idx index
    guards at the DB level — django-mail-auth authenticates by email.
    """

    add_form = UniqueEmailUserCreationForm
    form = UniqueEmailUserChangeForm


admin.site.unregister(User)
admin.site.register(User, MailAuthUserAdmin)
