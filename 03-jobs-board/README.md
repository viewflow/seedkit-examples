## Prompt

```
/django-seedkit

Project name: 03-jobs-board
Purpose: job board with background email notifications and a daily digest.

Settings layout: single file.
Database: PostgreSQL.
Postgres location: Postgres in Docker (`docker-compose.yml`).
Dev loop: `manage.py` in a `web` container via `docker compose`, not on the host.
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
  - tasks: Celery, with periodic tasks (Celery Beat). Also add a `jobs` app (`manage.py startapp jobs`), register `jobs` in `INSTALLED_APPS`, and add a sample `@shared_task` to `jobs/tasks.py` referenced from `CELERY_BEAT_SCHEDULE`.
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

Ship a `docker-compose.yml` with `web`, `worker`, `beat`, `db` and `redis` services, where only `web` publishes a host port. Run the foundation, build and start the stack, run migrate + createsuperuser through `web`, and define one trivial Celery task plus one Beat-scheduled task to prove autodiscovery works.
```

---

# 03 Jobs Board

Job board with background email notifications and a daily digest.

## Stack

- Django 6, single-file settings (`config/settings.py`), PostgreSQL via `django-environ`.
- Postgres + Redis run in Docker; `manage.py` also runs inside a `web` container — no host `uv run` loop.
- Auth: `django-mail-auth` passwordless magic-link, `mailauth.contrib.user.EmailUser` as `AUTH_USER_MODEL`.
- Background tasks: Celery + Celery Beat, broker/result backend on Redis (`/1`, `/2`). `jobs` app with a sample `@shared_task` wired into `CELERY_BEAT_SCHEDULE`.
- Email: console backend in dev (`EMAIL_URL=consolemail://`).
- i18n: `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS` wired; English only so far.
- Health checks: `/healthz` (liveness), `/readyz` (readiness — checks DB).
- Test runner: stock `manage.py test`.
- Task runner: `just`.

## Getting started

```sh
cp .env.example .env   # already done for local dev; edit if needed
just install           # docker compose build
just dev                # docker compose up — web + worker + beat + db + redis
```

In another terminal:

```sh
just migrate
just superuser
```

Open <http://localhost:8000/admin/> — sign in with the email you used for `createsuperuser` via the magic-link flow (check the `web` container logs for the login link; the console email backend prints it to stdout).

## Key commands

| Command | What it does |
| --- | --- |
| `just install` | Build the `web`/`worker`/`beat` images |
| `just dev` | Start the whole stack in the foreground |
| `just migrate` | Run migrations inside `web` |
| `just makemigrations` | Generate migrations inside `web` |
| `just test` | Run `manage.py test` inside `web` |
| `just shell` | Open `manage.py shell` inside `web` |
| `just superuser` | Create a superuser inside `web` |

Fallback without `just`: `docker compose exec -T web python manage.py <command>`.

Add background jobs to `jobs/tasks.py` as `@shared_task` functions; schedule periodic ones in `CELERY_BEAT_SCHEDULE` (`config/settings.py`).

Built with [Seedkit](https://github.com/viewflow/seedkit).
