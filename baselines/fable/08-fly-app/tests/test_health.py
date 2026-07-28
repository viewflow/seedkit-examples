import pytest
from django.test import Client


def test_healthz(client: Client) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content == b"ok"


@pytest.mark.django_db
def test_readyz(client: Client) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.content == b"ready"
