# 03-jobs-board

Job board with background email notifications and a daily digest.

## Stack

- Django (single settings file, `config/settings.py`)
- PostgreSQL and Redis in Docker (`docker-compose.yml`)
- Celery worker + Celery Beat for background email notifications and the daily digest
- Passwordless magic-link login via `django-mail-auth` (`/accounts/login/`)
- Console email backend in local development (`EMAIL_URL=consolemail://`)

## Quick start

```sh
just up          # start Postgres + Redis
just migrate     # apply migrations
just superuser   # create an admin account
just run         # http://127.0.0.1:8000/
```

Background tasks:

```sh
just worker      # Celery worker
just beat        # Celery Beat (schedules jobs.tasks.send_daily_digest daily at 07:00 UTC)
```

Health checks: `/healthz` (liveness), `/readyz` (readiness, checks the database).

Copy `.env.example` to `.env` to override settings; sane local defaults are built in.

## Tests

```sh
just test
```
