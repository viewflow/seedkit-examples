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

- Django 6, single-file settings (`config/settings.py`), `django-environ` for config.
- PostgreSQL in Docker (`docker-compose.yml`, published on `127.0.0.1:5432`).
- Auth: `django-mail-auth` (passwordless magic-link), `mailauth.contrib.user.EmailUser`.
- Background tasks: Celery + Celery Beat, Redis broker (`docker-compose.yml`, `127.0.0.1:6379`).
- Email: console backend in dev (`EMAIL_URL=consolemail://`).
- i18n enabled (`LANGUAGES`, `LocaleMiddleware`, `LOCALE_PATHS`).
- Health checks: `/healthz`, `/readyz`.
- Task runner: `just`.
- Tests: stock `manage.py test`.

## Setup

```sh
cp .env.example .env   # then edit DJANGO_SECRET_KEY for a real deploy
docker compose up -d
just install
just migrate
just superuser
just dev
```

Open <http://127.0.0.1:8000/admin/> and sign in with the superuser you just created.

In separate terminals, run the Celery worker and beat scheduler:

```sh
just worker
just beat
```

## Key commands

| Task | Command |
| --- | --- |
| `just install` | `uv sync` |
| `just dev` | `uv run manage.py runserver` |
| `just migrate` | `uv run manage.py migrate` |
| `just makemigrations` | `uv run manage.py makemigrations` |
| `just shell` | `uv run manage.py shell` |
| `just superuser` | `uv run manage.py createsuperuser` |
| `just test` | `uv run manage.py test` |
| `just worker` | `uv run celery -A config worker -l info` |
| `just beat` | `uv run celery -A config beat -l info` |

No task runner installed? Fall back to `uv run manage.py <command>`.

## Background tasks

`jobs/tasks.py` defines two sample `@shared_task` functions:

- `send_job_notification(job_id)` — ad-hoc task, call from views/signals when a job posting needs a notification sent.
- `send_daily_digest()` — scheduled via `CELERY_BEAT_SCHEDULE` in `config/settings.py` (runs daily at 08:00 UTC).

Drop real notification/digest logic into `jobs/tasks.py` as the job board grows.

## i18n

```sh
uv run manage.py makemessages -l de
uv run manage.py compilemessages
```

Requires GNU gettext installed on the host (`brew install gettext` / `apt-get install gettext`).

Built with [Seedkit](https://github.com/RobustaRush/seedkit).
