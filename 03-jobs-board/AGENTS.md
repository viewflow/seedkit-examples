# 03-jobs-board

Job board with background email notifications and a daily digest.

## Stack decisions

- Settings layout: single file (`config/settings.py`), env-driven via `django-environ`.
- Database: PostgreSQL, Postgres-in-Docker for local dev.
- Request handling: WSGI.
- Custom user model: no — stock `auth.User`.
- Auth: `django-mail-auth` (passwordless magic-link) against stock `auth.User`. `auth.User.email` has no unique constraint by default, so `jobs/migrations/0001_auth_user_email_unique.py` adds a partial unique index and `jobs/admin.py` overrides the admin's User forms to validate uniqueness too — otherwise two accounts could share an email and both receive magic-link tokens for it.
- i18n: enabled, `LANGUAGES = ["en"]`, no URL prefix.
- Cache: `django-redis` (`REDIS_URL/0`).
- Background tasks: Celery + Celery Beat, broker `REDIS_URL/1`, results `REDIS_URL/2`. Tasks live in `jobs/tasks.py`, autodiscovered via `app.autodiscover_tasks()` in `config/celery.py`.
- Email: console backend locally (`EMAIL_URL=consolemail://`).
- Health checks: `config/views.py` → `/healthz` (liveness), `/readyz` (DB readiness).
- Task runner: `just` (`justfile`).
- No REST API, no frontend, no CORS, no auth hardening (N/A — passwordless), no robots.txt, no django-extensions, no devcontainer, no production/deploy setup.

## Local ports

Host already ran Postgres (5432) and Redis (6379) natively, so
`docker-compose.yml` publishes this project's containers on **5433** and
**6380** instead. `.env` / `.env.example` `DATABASE_URL` / `REDIS_URL` match.

## Layout

```
config/
  settings.py       # single-file settings, env-driven
  celery.py         # Celery app, autodiscover_tasks()
  urls.py           # admin, mailauth accounts, healthz/readyz
  views.py          # liveness / readiness views
  wsgi.py / asgi.py
jobs/
  tasks.py          # @shared_task examples: add(), ping() (Beat-scheduled)
  admin.py          # UserAdmin override enforcing unique email
  migrations/0001_auth_user_email_unique.py
templates/registration/
  login.html, login_requested.html, logged_out.html   # django-mail-auth views
docker-compose.yml  # db (postgres:17) + redis, local dev only
justfile
```

## Key commands

```sh
just install            # uv sync
just dev                # runserver
just migrate            # apply migrations
just makemigrations     # generate migrations
just shell               # Django shell
just superuser           # createsuperuser
just test                # manage.py test
just worker               # celery worker
just beat                  # celery beat
```

Fallback without `just`: `uv run manage.py <command>`, `uv run celery -A config worker -l info`, `uv run celery -A config beat -l info`.

Local services: `docker compose up -d` (db + redis).
