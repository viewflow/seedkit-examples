import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_index_renders_tailwind_markup(client: Client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"text-blue-600" in response.content
    assert b"text-4xl" in response.content
    assert b'class="btn btn-primary"' in response.content
    assert b'data-theme="light"' in response.content


def test_index_has_seo_tags(client: Client) -> None:
    response = client.get("/")
    assert b'property="og:title"' in response.content
    assert b"favicon.svg" in response.content


def test_healthz(client: Client) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content == b"ok"


def test_readyz(client: Client) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.content == b"ready"


def test_robots_txt(client: Client) -> None:
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"User-agent: *" in response.content
    assert b"Sitemap:" in response.content


def test_sitemap(client: Client) -> None:
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert b"<urlset" in response.content
