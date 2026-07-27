## Prompt

```
/seedkit

Project name: 03-jobs-board
Purpose: job board with background email notifications and a daily digest.

Settings layout: single file.
Database: PostgreSQL.
Postgres location: Postgres in Docker (`docker-compose.yml`, port `127.0.0.1:5432` published to the host).
Lint with Ruff: no.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): yes.
Custom user model: no.
Auth add-on: `django-mail-auth` (passwordless magic-link).
Structured logging: no.
Task runner: just.
Add-ons:
  - redis (for Celery)
  - tasks: Celery, with periodic tasks (Celery Beat). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, and add a sample `@shared_task` to `jobs/tasks.py` referenced from `CELERY_BEAT_SCHEDULE`.
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - HTML email base template: no.
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: yes.
  - robots.txt: no.
  - django-extensions: no.
  - Devcontainer: no.

Production setup: skip.

Ship a `docker-compose.yml` with `db` and `redis` services only. Run the foundation, start the containers, run migrate + createsuperuser, and define one trivial Celery task plus one Beat-scheduled task to prove autodiscovery works.
```

---

# 03-jobs-board

Job board with background email notifications and a daily digest.

## Stack

- Django 6, single-file `config/settings.py`, `django-environ` for env-driven config.
- PostgreSQL 17 — Postgres in Docker (`docker-compose.yml`), host connects via the published port.
- Redis — cache (`django-redis`, DB `/0`) and Celery broker/results (DB `/1` / `/2`).
- Celery + Celery Beat — background tasks and periodic scheduling. `jobs` app registered in `INSTALLED_APPS`; `jobs/tasks.py` holds `@shared_task` functions, autodiscovered via `app.autodiscover_tasks()`.
- Auth: `django-mail-auth` — passwordless magic-link login (`mailauth.contrib.user.EmailUser` as `AUTH_USER_MODEL`; `mailauth.contrib.admin` wires the same flow into `/admin/`).
- Email: console backend in dev (`EMAIL_URL=consolemail://`) — magic links and notifications print to the `runserver` / worker stdout.
- i18n: `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS` wired; only `en` shipped — add locales with `uv run manage.py makemessages -l <code>`.
- Health checks: `/healthz` (liveness), `/readyz` (DB readiness) in `config/views.py`.
- Task runner: `just` (`justfile`).
- Test runner: stock `manage.py test`.

## Local ports

A native Postgres/Redis were already listening on the default ports (5432 / 6379) on the
dev machine this was scaffolded on, so the Docker services publish on **5433** / **6380**
instead. If your machine is clear of those, feel free to move `docker-compose.yml` and
`.env` back to the standard `5432` / `6379`.

## Setup

```sh
cp .env.example .env   # then set a real DJANGO_SECRET_KEY
docker compose up -d
just install
just migrate
just superuser
just dev
```

## Commands

| Command | Does |
| --- | --- |
| `just install` | `uv sync` |
| `just dev` | run the dev server |
| `just migrate` | apply migrations |
| `just makemigrations` | generate migrations |
| `just shell` | Django shell |
| `just superuser` | create a superuser |
| `just test` | `manage.py test` |
| `just worker` | run the Celery worker |
| `just beat` | run Celery Beat (periodic tasks) |

Fallback without `just`: `uv run manage.py <command>`.

Sign in at `/accounts/login/` (or `/admin/`) with any email — the magic link prints to
the console (dev) since `EMAIL_URL=consolemail://`.

## Background tasks

`jobs/tasks.py` ships one sample task, `send_daily_digest`, scheduled via
`CELERY_BEAT_SCHEDULE` in `config/settings.py` (daily at 08:00 UTC). Run a worker and
beat alongside `runserver`:

```sh
just worker
just beat
```

Built with [Seedkit](https://github.com/viewflow/seedkit).
