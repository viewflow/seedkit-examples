import json

from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # The export goes to the data subject — internal auth state stays out,
    # and the password hash above all.
    EXCLUDE = {"password", "is_staff", "is_superuser", "groups", "user_permissions"}

    def add_arguments(self, parser):
        parser.add_argument("user_id", type=int)

    def handle(self, *args, user_id, **opts):
        user = get_user_model().objects.get(pk=user_id)
        data = json.loads(serializers.serialize("json", [user]))
        for obj in data:
            obj["fields"] = {k: v for k, v in obj["fields"].items() if k not in self.EXCLUDE}
        self.stdout.write(json.dumps(data, indent=2))
