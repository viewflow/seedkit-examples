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

Production setup: VPS (Docker + Caddy). Use a multi-stage `Dockerfile` (uv builder → `python:3.12-slim-bookworm` runtime).

Assume Postgres is already running locally on port 5432 with user `postgres` / password `postgres`. Create database `shop_db` if missing (Postgres identifiers can't start with a digit, so use a clean name). Run the foundation + boot check, then run `python manage.py tailwind build` once so the CSS asset exists, and verify the index page returns the Tailwind-styled HTML.
```

---

## Prompt

```
/seedkit

Project name: 02-shop
Purpose: small e-commerce site with admin and SMTP transactional email.

Settings layout: split (config/settings/{base,local,production}.py).
Database: PostgreSQL, host Postgres (not docker). DB name `shop_db`.
Request handling: wsgi.
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: yes — custom `users.User` extending `AbstractUser`, app named `users`.
Auth add-on: `django-allauth` (email login, mandatory email verification, no social providers).
django-axes brute-force lockout: yes. 2FA: no.
Structured logging: no.
Task runner: mise.
Debug toolbar / DB safety tools / django-extensions / devcontainer: none.
Cache backend: locmem.
Background tasks: none.
Storage: WhiteNoise for static files only (no media volume yet, no S3).
Email: SMTP (console backend in local via EMAIL_URL=consolemail://, real SMTP in production).
CORS: no.
REST API: none.
Frontend: tailwind-cli standalone, with DaisyUI, custom 404/403/500 templates, agent-drawn SVG favicon.
  - `pages` app with an IndexView wired at `/`.
SEO (meta/OG tags + django.contrib.sitemaps): yes.
Billing: `stripe` raw SDK (not dj-stripe).
Health check endpoints (/healthz, /readyz): yes.
robots.txt: yes.
Security settings: yes, skip django-csp.
Error reporting: none. GDPR helpers: no. CI: not requested.
Deploy target: VPS (Docker + Caddy), multi-stage Dockerfile (uv builder → python:3.12-slim-bookworm runtime).
Database backups (django-dbbackup): yes.
```

---

# 02-shop

A small e-commerce reference build — admin, email-based accounts, and Stripe checkout.

## Stack

- **Django 6** with `django-environ`, split settings (`config/settings/{base,local,production,test}.py`)
- **Database**: PostgreSQL, host Postgres (`shop_db`)
- **Custom user model**: `users.User` (email as `USERNAME_FIELD`, no `username`)
- **Auth**: `django-allauth` (email login, mandatory verification in production) + `django-axes` (brute-force lockout). No 2FA.
- **Cache**: locmem (`LocMemCache`)
- **Static files**: WhiteNoise (compressed, manifest-hashed in production). No media storage backend wired (local `MEDIA_ROOT` only)
- **Email**: console backend in dev, SMTP in production (`EMAIL_URL`)
- **Billing**: Stripe raw SDK — checkout session, customer portal, and webhook views in `billing/`
- **Frontend**: Tailwind CSS via `django-tailwind-cli` (standalone binary, no Node/npm) + DaisyUI, custom 404/403/500 templates, agent-drawn SVG favicon
- **SEO**: meta/OG tags in `templates/base.html` + `django.contrib.sitemaps` at `/sitemap.xml`
- **`robots.txt`**: `/robots.txt`, gated on `DEBUG` / `ROBOTS_DISALLOW_ALL`
- **Health checks**: `/healthz` (liveness), `/readyz` (DB reachable)
- **Lint/format**: Ruff. **Types**: pyright + django-stubs. **Tests**: pytest + pytest-django
- **Task runner**: mise (`mise.toml`)
- **Security**: Django's HSTS/secure-cookie/SSL-redirect settings (no `django-csp`)
- **Database backups**: `django-dbbackup` to a local filesystem target (no S3 was requested for this project — see note under [Deploy](#deploy))
- **Deploy**: VPS via Docker + Caddy, multi-stage `Dockerfile` (`uv` builder → `python:3.12-slim-bookworm` runtime)

## Local development

Install [mise](https://mise.jdx.dev) (or run the underlying `uv run manage.py …` commands directly — see the fallback below). Requires a local PostgreSQL server.

```sh
cp .env.example .env   # then set a real DJANGO_SECRET_KEY
createdb shop_db

mise trust && mise install
mise run install
mise run migrate
mise run superuser
mise run tailwind        # tailwind watch + runserver, one process
```

Open <http://127.0.0.1:8000/admin/> and sign in with the new superuser.

| Task | Command |
| --- | --- |
| `mise run install` | `uv sync` |
| `mise run dev` | `uv run manage.py runserver` |
| `mise run migrate` | `uv run manage.py migrate` |
| `mise run makemigrations` | `uv run manage.py makemigrations` |
| `mise run shell` | `uv run manage.py shell` |
| `mise run superuser` | `uv run manage.py createsuperuser` |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run typecheck` | `uv run pyright` |
| `mise run collectstatic` | `uv run manage.py collectstatic --noinput` |
| `mise run tailwind` | `uv run manage.py tailwind runserver` |
| `mise run deploy` | see [Deploy](#deploy) |

No mise? Every task's command above runs directly with `uv run …`.

## Billing

Stripe checkout is wired against the raw SDK (no `dj-stripe`). Set `STRIPE_PUBLISHABLE_KEY` / `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` in `.env`. Local webhook testing:

```sh
stripe listen --forward-to localhost:8000/billing/webhook/
```

Paste the printed `whsec_...` into `STRIPE_WEBHOOK_SECRET`.

## Deploy

VPS with Docker + Caddy.

```sh
ssh user@vps
cd /srv/02-shop
git pull
# --env-file is required on every compose call — compose auto-loads only ./.env, not deploy/.env.prod
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
```

Copy `.env.example` to `deploy/.env.prod` on the VPS and fill in real values — `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DATABASE_URL` (pointing at the `db` service), a real `EMAIL_URL`, and the Stripe keys. Replace `example.com` in `deploy/Caddyfile` with the real domain before the first deploy.

`django-dbbackup` is wired against local filesystem storage inside the container (`DBBACKUP_STORAGE_DIR`, defaults to `/app/backups`) rather than S3 — no S3 target was in scope for this project. Mount `/app/backups` onto a persistent volume (already done in `deploy/docker-compose.prod.yml`) and copy backups off the VPS on your own schedule, or swap `DBBACKUP_STORAGE` for `storages.backends.s3boto3.S3Boto3Storage` if S3 comes into scope later.

## Environment variables

See `.env.example` for the full list.

---

Built with [Seedkit](https://github.com/RobustaRush/seedkit).
