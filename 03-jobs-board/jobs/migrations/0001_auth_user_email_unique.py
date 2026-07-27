from django.db import migrations


class Migration(migrations.Migration):
    """
    django-mail-auth authenticates against stock auth.User by email, which has
    no unique constraint. Two accounts sharing an address would both receive
    magic-link tokens for that address — this index closes that hijack path.
    """

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunSQL(
            sql="CREATE UNIQUE INDEX auth_user_email_unique_idx ON auth_user (email) WHERE email <> '';",
            reverse_sql="DROP INDEX auth_user_email_unique_idx;",
        ),
    ]
