## Prompt

```
/seedkit

Project name: 08-fly-app
Purpose: production app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.

Settings layout: split.
Database: PostgreSQL.
Postgres location: Postgres-in-Docker (`db` service alongside `redis` and `minio` in `docker-compose.yml`, port `127.0.0.1:5432` published).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: `django-mail-auth` (passwordless magic-link).
Structured logging: no.
Task runner: mise.
Add-ons:
  - redis
  - tasks: Celery
  - storage: S3-compatible (MinIO locally, real S3 in prod)
  - analytics: Google Analytics 4 (GA4)
  - email: anymail (Postmark provider). Install `django-anymail[postmark]`; set `EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"` only when not DEBUG; gate `POSTMARK_SERVER_TOKEN` from env. Wire `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`. Console backend stays as the `EMAIL_URL` fallback in dev. (django-mail-auth needs working email to send magic links.) Also include the Anymail webhook URL (`path("anymail/", include("anymail.urls"))`) and `ANYMAIL["WEBHOOK_SECRET"]`.
  - HTML email base template: no.
  - CORS: no.
  - REST API: `django-bolt` **with fast-path settings opt-in** (`uv add django-bolt`). Add `django_bolt` to `INSTALLED_APPS` in `base.py`. Create `config/settings/bolt.py` that imports from `base` and strips `SessionMiddleware`, `MessageMiddleware`, `CsrfViewMiddleware`, `AuthenticationMiddleware`, `WhiteNoiseMiddleware` from `MIDDLEWARE` and `django.contrib.admin`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles` from `INSTALLED_APPS`; sets `TEMPLATES = []` and `ROOT_URLCONF = 'config.urls_bolt'`. Create `config/urls_bolt.py` (API-only; no admin / accounts). Create an `api` app (`uv run manage.py startapp api`) with `api/api.py` exposing `BoltAPI()`, a single `GET /users/{user_id}` async handler returning a `msgspec.Struct` (`id`, `username`) populated via `await User.objects.aget(id=user_id)`. `runserver`/`gunicorn` keep using `config.settings.local` / `production`; `runbolt` runs against `config.settings.bolt`.
  - Frontend: none.
  - Auth hardening: `django-axes` (yes), 2FA (no).
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.
  - Devcontainer: no.

Production setup:
  - apply Django security settings
  - CSP via `django-csp`: yes
  - error reporting: GlitchTip via sentry-sdk
  - GDPR: PII scrubbing in error reports, retention defaults, user data export/delete views
  - CI: GitHub Actions test workflow
  - deploy target: Fly.io managed (use `[processes]` for web + worker + bolt; the `bolt` process runs `manage.py runbolt` with `DJANGO_SETTINGS_MODULE=config.settings.bolt`)
  - production Dockerfile: multi-stage (builder + slim runtime)

Run the foundation + boot check locally. Generate `Dockerfile`, `fly.toml`, `.github/workflows/test.yml`. Verify `docker build .` succeeds and the runtime stage uses `python:3.12-slim-bookworm`.
```

---

# 08-fly-app

Production app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.

## Stack

- Django 6, settings split into `config/settings/{base,local,production,test,bolt}.py`
- PostgreSQL (Postgres-in-Docker locally — `db` service in `docker-compose.yml`)
- Redis (cache + Celery broker/backend)
- Celery for background tasks
- S3-compatible storage for static + media (MinIO locally, real S3/R2/Spaces in prod)
- Auth: `django-mail-auth` (passwordless magic-link, `mailauth.contrib.user.EmailUser`)
- `django-axes` brute-force/lockout protection
- Email: `django-anymail` with Postmark (console backend in dev)
- Analytics: Google Analytics 4
- REST API: `django-bolt` with the fast-path settings opt-in (`config/settings/bolt.py`, `config/urls_bolt.py`, `api/api.py`)
- Ruff (lint + format), pytest + pytest-django, pyright + django-stubs
- Security hardening + CSP (`django-csp`) in production
- Error reporting: GlitchTip via `sentry-sdk`
- GDPR: PII scrubbing in Sentry events, user data export/delete management commands
- CI: GitHub Actions (`.github/workflows/test.yml`)
- Deploy: Fly.io managed (`fly.toml`, multi-stage `Dockerfile`)
- Task runner: mise (`mise.toml`)

## Setup

```sh
cp .env.example .env   # then set a real DJANGO_SECRET_KEY
docker compose up -d   # db + redis + minio
mise run install
mise run migrate
mise run dev            # http://127.0.0.1:8000
```

Without mise: `uv sync`, `uv run manage.py migrate`, `uv run manage.py runserver`.

### Local port map

The default ports (`5432`, `6379`, `9000`/`9001`) collided with other services
already running on this machine, so `docker-compose.yml` publishes:

| Service | Container port | Host port |
|---|---|---|
| Postgres | 5432 | 5433 |
| Redis | 6379 | 6380 |
| MinIO S3 API | 9000 | 9002 |
| MinIO console | 9001 | 9003 |

`.env` / `.env.example` already point at the remapped ports. Adjust them back to the
standard ports if your machine doesn't have the conflict.

## Commands

| Task | Command |
|---|---|
| Install deps | `mise run install` |
| Run dev server | `mise run dev` |
| Run migrations | `mise run migrate` |
| Make migrations | `mise run makemigrations` |
| Django shell | `mise run shell` |
| Create superuser | `mise run superuser` |
| Run tests | `mise run test` |
| Lint | `mise run lint` |
| Format | `mise run fmt` |
| Type check | `mise run typecheck` |
| Collect static | `mise run collectstatic` |
| Celery worker | `mise run worker` |
| Deploy (Fly) | `mise run deploy` |

Fallback without mise: `uv run manage.py <command>`.

### django-bolt API

Two servers, two ports:

```sh
uv run manage.py runserver                                                  # admin + classic views, :8000
DJANGO_SETTINGS_MODULE=config.settings.bolt uv run manage.py runbolt --dev --port 8001   # API, :8001
```

`GET /users/{user_id}` on the bolt server returns `{"id": ..., "username": ...}` — populated
from `mailauth.contrib.user.EmailUser`, whose `email` field fills the `username` slot (the
project's auth is email-only, passwordless — there's no separate username column).

## GDPR

```sh
uv run manage.py export_user_data <user_id>
uv run manage.py delete_user_data <user_id>
```

## Deploy

```sh
fly launch --no-deploy
fly postgres create
fly postgres attach <db-name>
fly redis create
fly redis attach <redis-name>
fly secrets set \
    DJANGO_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))') \
    DJANGO_ALLOWED_HOSTS=$(fly status -j | jq -r '.Hostname'),example.com \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com \
    EMAIL_URL=consolemail:// \
    POSTMARK_SERVER_TOKEN=... \
    AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... AWS_STORAGE_BUCKET_NAME=... AWS_S3_REGION_NAME=... \
    SENTRY_DSN=... \
    ANALYTICS_ID=G-XXXXXXX
fly deploy
```

`fly.toml`'s `release_command` runs `migrate` + `collectstatic` before every deploy.
`[processes]` runs `web` (gunicorn), `worker` (Celery), and `bolt` (`runbolt` under
`config.settings.bolt`) as separate Fly processes.

Built with [Seedkit](https://github.com/viewflow/seedkit).
