import pytest
from django.contrib.auth.models import User
from django_bolt.testing import TestClient

from api.api import api


@pytest.mark.django_db(transaction=True)
def test_get_user():
    user = User.objects.create_user(username="alice", password="pw")

    with TestClient(api) as client:
        response = client.get(f"/users/{user.pk}")

    assert response.status_code == 200
    assert response.json() == {"id": user.pk, "username": "alice"}
