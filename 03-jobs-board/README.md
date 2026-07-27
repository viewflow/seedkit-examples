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

- Django 6, single-file settings (`config/settings.py`)
- PostgreSQL (Postgres-in-Docker for local dev)
- Auth: `django-mail-auth` (passwordless magic-link) against stock `auth.User`, with a DB-level unique index + admin-form validation on email (`jobs/migrations/0001_auth_user_email_unique.py`, `jobs/admin.py`) since `auth.User.email` has no built-in uniqueness
- Background tasks: Celery + Celery Beat, broker/results on Redis, autodiscovered from `jobs/tasks.py`
- Cache: `django-redis`
- Email: console backend locally (`EMAIL_URL=consolemail://`)
- i18n enabled (`LANGUAGES = ["en"]` — add more as the product ships them)
- Health checks: `/healthz` (liveness), `/readyz` (DB readiness)
- Task runner: `just`

## Setup

```sh
cp .env.example .env   # then set a real DJANGO_SECRET_KEY
docker compose up -d
just install
just migrate
just superuser
just dev
```

Open <http://127.0.0.1:8000/admin/> and sign in — the magic link prints to the
`runserver` console (console email backend).

## Commands

```sh
just install          # uv sync
just dev               # runserver
just migrate           # apply migrations
just makemigrations    # generate migrations
just shell              # Django shell
just superuser          # createsuperuser
just test               # manage.py test
just worker             # celery worker
just beat                # celery beat (periodic tasks)
```

Fallback without `just`: `uv run manage.py <command>`.

Run the worker and beat in separate terminals alongside `just dev`:

```sh
just worker
just beat
```

## Local ports

The host already had Postgres and Redis listening on the default ports
(5432 / 6379), so this project's `docker-compose.yml` publishes them on
**5433** and **6380** instead — `.env` / `.env.example` match. Adjust back to
5432/6380 if your host is free of conflicts.

## Tasks

Add `@shared_task` functions to `jobs/tasks.py`; Celery autodiscovers them
from any app in `INSTALLED_APPS`. `jobs/tasks.py` ships two examples:

- `add(x, y)` — trivial task, call with `.delay(1, 2)`
- `ping()` — scheduled every minute via `CELERY_BEAT_SCHEDULE` in
  `config/settings.py`, proving Beat + autodiscovery work end to end

## Production setup

Not configured — this project only ships local dev services
(`docker-compose.yml` with `db` + `redis`). Add a production Dockerfile,
deploy target, and security settings when the project is ready to ship.

Built with [Seedkit](https://github.com/viewflow/seedkit).
