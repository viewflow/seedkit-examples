# Shop

Small e-commerce site: Django 5.2, PostgreSQL, django-allauth (email login with
mandatory verification), django-axes, Stripe SDK, Tailwind CSS 4 + DaisyUI via
django-tailwind-cli, WhiteNoise, SMTP transactional email.

## Development

Requires [uv](https://docs.astral.sh/uv/), [mise](https://mise.jdx.dev/) and a
local PostgreSQL on port 5432 (user `postgres` / password `postgres`).

```sh
mise run setup   # uv sync, createdb shop_db, migrate
mise run dev     # runserver + Tailwind watcher (browser auto-reload enabled)
```

Other tasks: `mise run test`, `mise run lint`, `mise run typecheck`,
`mise run css` (one-off Tailwind build).

Settings live in `config/settings/` — `base.py`, `local.py` (default for
`manage.py`), `production.py` (default for WSGI/ASGI). Email prints to the
console locally and goes out via SMTP in production (see `.env.example`).

## Production

Multi-stage `Dockerfile` (uv builder → `python:3.12-slim-bookworm`) serving via
gunicorn + WhiteNoise behind Caddy:

```sh
cp .env.example .env  # fill in real values
docker compose up -d --build
```
