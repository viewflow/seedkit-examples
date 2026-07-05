import pytest


@pytest.mark.django_db
def test_index_smoke(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"text-blue-600" in response.content
