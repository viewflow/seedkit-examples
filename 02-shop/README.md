## Prompt

```
/seedkit

Project name: 02-shop
Purpose: small e-commerce site with admin and SMTP transactional email.

Settings layout: split (`config/settings/base.py`, `local.py`, `production.py`).
Database: PostgreSQL.
Postgres location: on the host (use `createdb` for the project DB).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: yes (custom `users.User` extending `AbstractUser`).
Auth add-on: `django-allauth` (email login, mandatory email verification, no social providers).
Structured logging: no.
Task runner: mise.
Add-ons:
  - storage: WhiteNoise for static files (no media volume yet)
  - email: SMTP (console backend in local, SMTP in production)
  - HTML email base template: no.
  - CORS: no.
  - REST API: none.
  - Frontend: `tailwind-cli` (custom 404/403/500 templates: yes; DaisyUI: yes; favicon: yes — agent-drawn SVG). Also add a `pages` app with an `IndexView(TemplateView)` wired at `/`. Its `index.html` must include `text-blue-600` and `text-4xl` (utility check) and a `<button class="btn btn-primary">` (DaisyUI check) — concrete grep targets for the integration tests below.
  - SEO (meta/OG tags + sitemap): yes. The sitemap lists the `pages` index URL.
  - Auth hardening: `django-axes` (yes), 2FA (no).
  - Billing: `stripe` raw SDK.
  - Health check endpoints: yes.
  - `robots.txt`: yes.
  - `django-extensions`: no.
  - Browser auto-reload: yes (`django-browser-reload`).

Production setup: VPS (Docker + Caddy). Use a multi-stage `Dockerfile` (uv builder → `python:3.12-slim-bookworm` runtime).

Assume Postgres is already running locally on port 5432 with user `postgres` / password `postgres`. Create database `shop_db` if missing (Postgres identifiers can't start with a digit, so use a clean name). Run the foundation + boot check, then run `python manage.py tailwind build` once so the CSS asset exists, and verify the index page returns the Tailwind-styled HTML.
```

---

# Shop

Small e-commerce site with admin and SMTP transactional email.

## Stack

- Django 6, split settings (`config/settings/base.py`, `local.py`, `production.py`, `test.py`)
- PostgreSQL via `django-environ` (`DATABASE_URL`), host Postgres in dev
- Custom user model (`users.User`, email login, no username)
- `django-allauth` — email login, mandatory email verification in production
- `django-axes` — brute-force lockout on the login path
- WhiteNoise — compressed manifest static storage in production
- SMTP email (console backend in dev, SMTP in production) via `EMAIL_URL`
- `django-tailwind-cli` + DaisyUI — no Node/npm; custom 404/403/500 templates; agent-drawn SVG favicon
- `pages` app — `IndexView` at `/`
- SEO — meta/OG tags in `base.html`, `sitemap.xml` via `django.contrib.sitemaps`
- `robots.txt` — disallows `/admin/` and `/accounts/` in production, disallow-all in dev
- `stripe` (raw SDK) — Stripe Customer, Checkout, Customer Portal, and webhook views in `billing/`
- Health checks — `/healthz` (liveness), `/readyz` (DB readiness)
- `django-browser-reload` — dev-only tab auto-refresh
- Ruff (lint + format), pytest + pytest-django, pyright + django-stubs
- Task runner: mise (`mise.toml`)
- Production: multi-stage `Dockerfile` (uv builder → `python:3.12-slim-bookworm` runtime), VPS deploy via Docker Compose + Caddy

## Key commands

```sh
mise run install         # uv sync
mise run dev              # runserver
mise run migrate          # manage.py migrate
mise run makemigrations
mise run shell
mise run superuser
mise run test              # pytest
mise run lint              # ruff check
mise run fmt                # ruff format
mise run typecheck         # pyright
mise run collectstatic
mise run tailwind           # tailwind runserver (watch + dev server)
```

Fallback without mise: `uv run manage.py <command>`.

First-time setup:

```sh
mise trust && mise install
cp .env.example .env
createdb shop_db
uv run manage.py migrate
uv run manage.py tailwind build
uv run manage.py createsuperuser
```

## Deploy

```sh
ssh user@vps
cd /srv/shop
git pull
# --env-file is required on every compose call — compose auto-loads only ./.env, not deploy/.env.prod
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
docker image prune -f   # old :latest layers otherwise accumulate until the disk fills
```

Or via the task runner: `mise run deploy` (runs `deploy-migrate` first, then `up -d`).

Copy `deploy/.env.prod.example` to `deploy/.env.prod` on the VPS and fill in real secrets before the first deploy. Replace `example.com` in `deploy/Caddyfile` and the `{owner}` placeholder in `deploy/docker-compose.prod.yml`'s image line with the real GHCR owner.

Built with [Seedkit](https://github.com/viewflow/seedkit).
