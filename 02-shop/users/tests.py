import pytest


@pytest.mark.django_db
def test_smoke(client):
    assert client.get("/healthz").status_code == 200
