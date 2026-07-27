# silk-lab

Profile a few request paths with [django-silk](https://github.com/jazzband/django-silk)
and run a simple background email task on the [Django Tasks](https://docs.djangoproject.com/en/stable/topics/tasks/)
database backend ([django-tasks-db](https://github.com/RealOrangeOne/django-tasks-db)).

## Stack

- Django 6 + PostgreSQL (`psycopg`)
- Split settings: `config.settings.{base,local,test}`
- `django-silk` — request profiling, `/silk/`
- `django-tasks` + `django-tasks-db` — background tasks on the DB backend, `jobs` app
- `django-extensions`
- `django-zeal` — N+1 query detection (dev/test only)
- `django-migration-linter` — `lintmigrations` (limited to first-party apps)
- `django-test-migrations` — pytest plugin for migration tests
- GoatCounter — self-hosted analytics snippet, env-driven site code
- Ruff, pytest (`pytest-django`)

## Setup

```sh
createdb silk_db
cp .env.example .env   # adjust as needed
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Running

```sh
uv run manage.py runserver
```

In a second terminal, run the task worker:

```sh
uv run manage.py db_worker
```

Enqueue the sample task from a shell:

```sh
uv run manage.py shell -c "
from jobs.tasks import send_welcome_email
send_welcome_email.enqueue('someone@example.com')
"
```

The worker terminal will print the email via the console backend and mark the task `SUCCESSFUL`.

Visit `/` for a view decorated with `@silk_profile`, then check `/silk/` for the
profiling data.

## Health checks

- `/healthz` — liveness, always `ok`
- `/readyz` — readiness, runs `SELECT 1` against the database, returns `ready`

## Checks

```sh
uv run ruff check .
uv run manage.py lintmigrations
uv run pytest
```
