# Shop

Small e-commerce site with admin and SMTP transactional email, built with Django.

## Stack

- Django 6, PostgreSQL, custom `users.User` model (email login)
- `django-allauth` (email login, mandatory verification, no social providers)
- `django-axes` for login-attempt lockout
- `django-tailwind-cli` + DaisyUI for styling, `django-browser-reload` in dev
- WhiteNoise for static files
- `stripe` (raw SDK) for billing
- Health checks at `/healthz` and `/readyz`, `robots.txt`, `sitemap.xml`, OG tags

## Local setup

```sh
createdb shop_db
cp .env.example .env
uv sync
uv run manage.py migrate
uv run manage.py tailwind build
uv run manage.py createsuperuser
uv run manage.py runserver
```

Or via `mise`:

```sh
mise run install
mise run migrate
mise run css
mise run dev
```

## Tests, lint, type check

```sh
uv run pytest
uv run ruff check .
uv run pyright
```

## Production

Multi-stage `Dockerfile` (uv builder → `python:3.12-slim-bookworm` runtime), deployed
behind Caddy on a VPS — see `deploy/Caddyfile` and `deploy/docker-compose.prod.yml`.
