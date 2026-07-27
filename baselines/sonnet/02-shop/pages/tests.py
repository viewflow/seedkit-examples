import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index_view_renders(client):
    response = client.get(reverse("pages:index"))

    assert response.status_code == 200
    assert b"Welcome to Shop" in response.content
