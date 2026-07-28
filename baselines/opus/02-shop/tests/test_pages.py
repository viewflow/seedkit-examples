"""The public surface: index page, SEO, health checks, static assets."""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_index_renders_with_tailwind_and_daisyui(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.content.decode()

    assert "text-blue-600" in body  # a plain Tailwind utility
    assert "text-4xl" in body
    assert 'class="btn btn-primary"' in body  # a DaisyUI component
    assert "data-theme=" in body
    assert "favicon.svg" in body


@pytest.mark.django_db
def test_index_has_seo_tags(client):
    body = client.get("/").content.decode()
    assert 'property="og:title"' in body
    assert 'name="description"' in body
    assert 'rel="canonical"' in body


@pytest.mark.django_db  # ATOMIC_REQUESTS opens a transaction for every request
def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.content == b"ok"


@pytest.mark.django_db
def test_readyz_reports_database(client):
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.content == b"ready"


@pytest.mark.django_db
def test_robots_txt(client):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert "User-agent: *" in response.content.decode()
    assert response["Content-Type"].startswith("text/plain")


@pytest.mark.django_db
def test_sitemap_lists_the_index_page(client, product):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    body = response.content.decode()
    assert "<urlset" in body
    assert reverse("pages:index") in body
    assert product.get_absolute_url() in body
