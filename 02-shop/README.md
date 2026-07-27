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

# 02-shop

Small e-commerce site with admin and SMTP transactional email.

## Stack

- Django 6, split settings (`config/settings/base.py` / `local.py` / `production.py` / `test.py`)
- PostgreSQL (host-installed, `DATABASE_URL`)
- Custom user model — `users.User` (email login, no username field)
- Auth: `django-allauth` (email login, mandatory email verification in production), `django-axes` brute-force lockout
- Frontend: `django-tailwind-cli` + DaisyUI, custom 404/403/500 templates, agent-drawn SVG favicon
- `pages` app with `IndexView` at `/`
- SEO: meta/OG tags + `django.contrib.sitemaps` (`/sitemap.xml`)
- `robots.txt`
- Static files: WhiteNoise (compressed manifest storage in production)
- Email: console backend in dev, SMTP in production (`EMAIL_URL`)
- Billing: raw `stripe` SDK (Stripe-hosted Checkout + Customer Portal)
- Health checks: `/healthz` (liveness), `/readyz` (DB reachability)
- Dev: Ruff, pytest + pytest-django, pyright + django-stubs, django-browser-reload
- Task runner: mise
- Production: multi-stage Docker (uv builder → `python:3.12-slim-bookworm`), deployed via Docker Compose + Caddy on a VPS

## Setup

```sh
cp .env.example .env          # edit DJANGO_SECRET_KEY / DATABASE_URL as needed
createdb shop_db
mise trust && mise install
mise run install
mise run migrate
mise run tailwind              # first run downloads the Tailwind CLI binary
mise run dev
```

Without mise: `uv sync`, `uv run manage.py migrate`, `uv run manage.py tailwind runserver`.

## Commands

| Task | mise | Fallback |
| --- | --- | --- |
| Install deps | `mise run install` | `uv sync` |
| Run dev server | `mise run dev` | `uv run manage.py runserver` |
| Migrate | `mise run migrate` | `uv run manage.py migrate` |
| Make migrations | `mise run makemigrations` | `uv run manage.py makemigrations` |
| Shell | `mise run shell` | `uv run manage.py shell` |
| Create superuser | `mise run superuser` | `uv run manage.py createsuperuser` |
| Test | `mise run test` | `uv run pytest` |
| Lint | `mise run lint` | `uv run ruff check .` |
| Format | `mise run fmt` | `uv run ruff format .` |
| Typecheck | `mise run typecheck` | `uv run pyright` |
| Collect static | `mise run collectstatic` | `uv run manage.py collectstatic --noinput` |
| Tailwind (watch + runserver) | `mise run tailwind` | `uv run manage.py tailwind runserver` |

## Stripe

Set `STRIPE_PUBLISHABLE_KEY` / `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` in `.env`. For local webhook testing:

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
```

## Deploy

VPS with Docker + Caddy. `deploy/docker-compose.prod.yml` runs `web` (gunicorn, from the image built by the root `Dockerfile`), `db` (Postgres 17), and `caddy` (TLS termination + reverse proxy). Copy `deploy/.env.prod.example` to `deploy/.env.prod` on the server and fill in real values first.

```sh
ssh user@vps
cd /srv/02-shop
git pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
docker image prune -f
```

Or via mise: `mise run deploy` (runs `deploy-migrate` first, then `up -d`).

Replace `example.com` in `deploy/Caddyfile` and the `image:` line in `deploy/docker-compose.prod.yml` with the real domain / registry path before the first deploy.

Built with [Seedkit](https://github.com/viewflow/seedkit).
