# Jobs Board

A job board with background email notifications and a daily digest, built with
Django, Celery, and PostgreSQL.

## Stack

- Django 6, PostgreSQL, single-file settings (`config/settings.py`)
- `django-mail-auth` for passwordless (magic-link) login
- Celery + Celery Beat for background jobs and the daily digest, Redis as the broker
- `just` as the task runner

## Getting started

```sh
cp .env.example .env
just up            # start Postgres + Redis in Docker
just migrate
just createsuperuser
just run           # http://127.0.0.1:8000
```

In separate terminals, to run background jobs:

```sh
just worker
just beat
```

## Notifications

- `jobs.tasks.notify_new_job` fires whenever a `Job` is created (see `jobs/signals.py`).
- `jobs.tasks.send_daily_digest` runs once a day at 06:00 UTC via Celery Beat
  (see `CELERY_BEAT_SCHEDULE` in `config/settings.py`).

## Health checks

- `/healthz` — liveness, always returns `ok`.
- `/readyz` — readiness, checks the database connection and returns `ready`.

## Email

Locally, email is printed to the console (`EMAIL_URL=consolemail://` in `.env`).
Point `EMAIL_URL` at a real backend (e.g. `smtp://user:pass@host:587`) in other
environments.

## Tests

```sh
just test
```
