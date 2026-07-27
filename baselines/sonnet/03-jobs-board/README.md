# 03-jobs-board

Job board with background email notifications and a daily digest.

## Stack

- Django 6, single-file settings (`config/settings.py`)
- PostgreSQL (via `psycopg`), running in Docker
- Redis + Celery + Celery Beat for background/periodic tasks
- `django-mail-auth` for passwordless (magic-link) authentication
- Console email backend locally
- Health check endpoints: `/healthz`, `/readyz`
- i18n enabled
- `just` as the task runner

## Getting started

```sh
cp .env.example .env
docker compose up -d
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Or via `just`:

```sh
just up
just migrate
just run
```

Log in at `/accounts/login/` with an email address — a login link is printed to
the console (local email backend). The Django admin at `/admin/` still accepts
username/password for the superuser account.

## Background tasks

Run a worker and the Beat scheduler alongside the dev server:

```sh
just worker
just beat
```

`jobs/tasks.py` has a sample `send_application_notification` task and a
`send_daily_digest` task wired into `CELERY_BEAT_SCHEDULE` (settings.py) to run
daily at 07:00 UTC.

## Tests

```sh
just test
```
