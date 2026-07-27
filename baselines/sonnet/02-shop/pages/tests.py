import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestIndexView:
    def test_get(self, client):
        response = client.get(reverse("pages:index"))
        assert response.status_code == 200
        assert b"text-blue-600" in response.content
        assert b"text-4xl" in response.content
        assert b'btn btn-primary' in response.content
