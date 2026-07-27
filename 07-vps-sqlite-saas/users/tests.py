import pytest


@pytest.mark.django_db
def test_smoke(client):
    assert client.get("/admin/login/").status_code == 200
