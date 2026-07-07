# Shop

A small e-commerce site: Django admin, email/password auth (mandatory email
verification), SMTP transactional email, Stripe billing, and a Tailwind +
DaisyUI storefront.

## Stack

- Django 5.1, PostgreSQL
- `django-allauth` — email-based login, mandatory email verification
- `django-axes` — brute-force login protection
- `stripe` — raw SDK for billing
- `django-tailwind-cli` — Tailwind v4 + DaisyUI, no Node.js required
- WhiteNoise — static file serving
- `uv` for dependency management, `mise` as the task runner
- `pytest` + `pytest-django` for tests, `ruff` for lint/format, `pyright` +
  `django-stubs` for type checking

## Local development

Requires PostgreSQL running locally (`user=postgres`, `password=postgres`) and
[`mise`](https://mise.jdx.dev)/[`uv`](https://docs.astral.sh/uv/) installed.

```bash
createdb shop_db

cp .env.example .env      # adjust values as needed

mise run install          # uv sync
mise run migrate
mise run tailwind-build    # or `tailwind-watch` while developing
mise run run               # http://localhost:8000
```

Common tasks (see `mise.toml` / `mise tasks`):

```bash
mise run test        # pytest
mise run lint         # ruff check
mise run format       # ruff format
mise run typecheck    # pyright
mise run check        # lint + typecheck + test
```

## Configuration

Settings are split under `config/settings/`:

- `base.py` — shared configuration
- `local.py` — local development (console email backend, weak password hasher)
- `production.py` — hardened for deployment (HSTS, secure cookies, SSL redirect)

All secrets/environment-specific values are read from the environment (see
`.env.example`). `manage.py` and local scripts default to
`config.settings.local`; `wsgi.py`/`asgi.py` default to
`config.settings.production`.

## Deployment (VPS: Docker + Caddy)

The app ships as a multi-stage Docker image (`uv` builder → slim Python 3.12
runtime) served by `gunicorn`, fronted by Caddy for TLS termination.

Postgres is expected to run on the host VPS (not in a container). The `web`
container reaches it via `host.docker.internal`.

```bash
cp .env.example .env   # fill in real secrets, DATABASE_URL, SITE_DOMAIN, etc.
docker compose up -d --build
```

On start, the container runs pending migrations, then serves via `gunicorn`
on port 8000 behind Caddy (ports 80/443).

## Health check

`GET /healthz/` returns `200 OK` if the app can reach the database.
