import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index_renders_tailwind_and_daisyui(client):
    response = client.get(reverse("pages:index"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "text-blue-600" in content
    assert "text-4xl" in content
    assert '<button class="btn btn-primary">' in content


@pytest.mark.django_db
def test_robots_txt(client):
    response = client.get("/robots.txt")

    assert response.status_code == 200
    assert response["content-type"].startswith("text/plain")
    assert b"Disallow: /admin/" in response.content


@pytest.mark.django_db
def test_sitemap(client):
    response = client.get("/sitemap.xml")

    assert response.status_code == 200
    assert b"<urlset" in response.content
