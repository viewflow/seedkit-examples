## Prompt

```
/seedkit

Project name: 06-silk-lab
Purpose: profile a few request paths with django-silk and run a simple background email task on the DB backend.

Settings layout: split.
Database: PostgreSQL.
Postgres location: on the host (use `createdb silk_db`).
Lint with Ruff: yes.
Test runner: pytest (required for django-test-migrations).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: no.
Task runner: none.
Add-ons:
  - debug: django-silk (profiling + `@silk_profile`)
  - tasks: Django Tasks with the Database backend (`django-tasks-db`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - analytics: GoatCounter (self-hosted snippet, env-driven site code)
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - HTML email base template: no.
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Devcontainer: no.
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: yes.
  - Database safety tools: all three —
      - django-zeal: yes
      - django-migration-linter: yes
      - django-test-migrations: yes

Production setup: skip.

Run the foundation, the boot check, start `manage.py db_worker` in a second terminal, enqueue one example task and confirm it runs. Hit a profiled view and confirm the request appears under `/silk/`. Run `uv run manage.py lintmigrations`. Run `uv run pytest` to confirm the test runner is wired (no project-specific tests required — `django-test-migrations` is installed for the user to write migration tests later).
```

---

# 06-silk-lab

Profile a few request paths with django-silk and run a simple background email task on the DB backend.

## Stack

- Django 6, split settings (`config/settings/base.py` / `local.py` / `production.py` / `test.py`)
- PostgreSQL (host-installed) via `DATABASE_URL`
- Ruff for linting/formatting
- pytest + pytest-django for tests
- django-silk — profiling dashboard at `/silk/`, `@silk_profile` demo in `jobs/views.py`
- Django Tasks with the Database backend (`django-tasks-db`) — `jobs` app, worker via `manage.py db_worker`
- GoatCounter analytics (env-driven, disabled until `ANALYTICS_ID`/`ANALYTICS_HOST` are set)
- Console email backend in local dev (`EMAIL_URL=consolemail://`)
- Health checks: `/healthz` (liveness), `/readyz` (DB readiness)
- django-extensions, django-zeal, django-migration-linter, django-test-migrations (all dev-only)

## Setup

```sh
createdb silk_db
cp .env.example .env   # then set DJANGO_SECRET_KEY and DATABASE_URL
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
uv run manage.py runserver
```

In a second terminal, start the task worker:

```sh
uv run manage.py db_worker
```

## Try it

- Admin: <http://localhost:8000/admin/>
- Silk profiling dashboard: <http://localhost:8000/silk/>
- Profiled demo view (shows up in Silk, uses `@silk_profile`): <http://localhost:8000/jobs/profile-demo/>
- Enqueue the sample email task:

  ```sh
  uv run manage.py shell -c "from jobs.tasks import send_welcome_email; send_welcome_email.enqueue('someone@example.com')"
  ```

  Watch the `db_worker` terminal — the email prints to stdout via the console backend.

## Key commands

```sh
uv run manage.py migrate
uv run manage.py runserver
uv run manage.py db_worker
uv run manage.py lintmigrations
uv run ruff check .
uv run ruff format .
uv run pytest
```

Built with [Seedkit](https://github.com/viewflow/seedkit).
