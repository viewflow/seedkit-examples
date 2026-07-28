# 03-jobs-board

A job board with background email notifications and a daily digest.

- Django 5.2, single-file settings (`config/settings.py`)
- PostgreSQL and Redis in Docker
- Celery for background work, Celery Beat for the daily digest
- Passwordless sign-in via [django-mail-auth](https://github.com/django-mail-auth/django-mail-auth)
- Console email backend locally (`EMAIL_URL=consolemail://`)
- `/healthz` and `/readyz` probes
- i18n enabled (English and German catalogues under `locale/`)

## Getting started

```sh
cp .env.example .env      # adjust POSTGRES_PORT / REDIS_PORT if they clash
just install              # uv sync
just up                   # start Postgres + Redis
just migrate
just superuser
just run                  # http://127.0.0.1:8000/
```

Run `just` on its own to see every recipe.

### Background workers

Celery needs two processes, each in its own terminal:

```sh
just worker   # celery -A config worker
just beat     # celery -A config beat
```

The scheduler is `django_celery_beat`'s `DatabaseScheduler`, so `just migrate`
must run before `just beat`. Entries in `CELERY_BEAT_SCHEDULE` are synced into
the database on the first beat startup and are editable afterwards in the admin
under *Periodic Tasks*.

## Layout

```
config/          settings, urls, celery app, health probes
jobs/            the job board app (models, views, tasks, admin, tests)
templates/       base layout, job pages, magic-link login + email bodies
locale/          en/de message catalogues
```

## Background tasks

| Task | Trigger |
| --- | --- |
| `jobs.tasks.send_job_posted_notification` | Admin action "Publish selected jobs" |
| `jobs.tasks.send_daily_digest` | Celery Beat, daily at 07:00 UTC |

With `EMAIL_URL=consolemail://` the messages are printed to the worker's stdout
rather than sent.

## Ports

`docker-compose.yml` publishes Postgres on `127.0.0.1:5432` and Redis on
`127.0.0.1:6379` by default. Both are overridable with `POSTGRES_PORT` and
`REDIS_PORT` for machines that already run those services — the local `.env`
shifts them to `5433`/`6380` for exactly that reason. Keep `DATABASE_URL` and
`REDIS_URL` in sync when you change them.

## Tests

```sh
just test
```
