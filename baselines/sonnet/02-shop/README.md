# Shop

A small Django e-commerce site with an admin, SMTP transactional email, and Stripe billing.

## Stack

- Django 5.1, PostgreSQL
- django-allauth (email login, mandatory email verification)
- django-axes (login-attempt lockouts)
- Tailwind CSS + DaisyUI via django-tailwind-cli
- WhiteNoise for static files
- Stripe (raw SDK)
- pytest + pytest-django, Ruff, pyright (django-stubs)

## Local development

```sh
createdb shop_db
uv sync
uv run manage.py migrate
uv run manage.py tailwind build
uv run manage.py createsuperuser
uv run manage.py runserver
```

Or via mise:

```sh
mise run setup
mise run migrate
mise run tailwind
mise run dev
```

Copy `.env.example` to `.env` and adjust values as needed; local defaults work out of the box against a local Postgres instance.

## Tests, lint, types

```sh
uv run pytest
uv run ruff check .
uv run pyright
```

## Production

Build and run with Docker (multi-stage build, Caddy reverse proxy):

```sh
cd deploy
docker compose -f docker-compose.prod.yml up -d --build
```

Set the required variables in `.env` first (see `.env.example`).
