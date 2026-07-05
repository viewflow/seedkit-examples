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
```

---

# 06-silk-lab

Profile a few request paths with django-silk and run a simple background email task on the DB backend.

- Settings layout: split (`config/settings/{base,local,production,test}.py`).
- Database: PostgreSQL, host Postgres (not Docker). Dev DB name `silk_db`.
- Request handling: WSGI.
- Custom user model: none.
- Auth: none.
- Cache: Django's default (`LocMemCache`), not explicitly configured.
- Background tasks: Django Tasks (`django.tasks` API) with the `django-tasks-db` database backend. **Note:** the current `django-tasks-db` 0.12.0 release still depends on the standalone `django-tasks` backport package (not Django 6's built-in `django.tasks`) — tasks are defined with `from django_tasks import task`, not `from django.tasks import task`. See `jobs/tasks.py`.
- Debug toolbar: django-silk, profiling dashboard at `/silk/`.
- Database safety: `django-zeal` (N+1 detection), `django-migration-linter` (`lintmigrations`), `django-test-migrations` (`migrator` pytest fixture).
- `django-extensions`: yes (`shell_plus`, `runserver_plus`, `show_urls`, …).
- Email: console backend in dev (`EMAIL_URL=consolemail://`). No HTML email base template.
- Analytics: GoatCounter, env-driven `ANALYTICS_ID` / `ANALYTICS_HOST`, gated on `not DEBUG`.
- Health checks: `/healthz` (liveness), `/readyz` (DB reachable).
- Lint: Ruff. Tests: pytest + pytest-django. No type checking, no pre-commit hooks, no i18n, no CI.
- Task runner: none — use `uv run manage.py …` directly.

## Layout

```
06-silk-lab/
├── config/
│   ├── settings/{base,local,production,test}.py
│   ├── context_processors.py  # analytics
│   ├── urls.py
│   ├── views.py                # healthz, readyz
│   ├── wsgi.py / asgi.py
├── jobs/                       # django-tasks-db worker tasks
│   ├── apps.py                 # ready() imports tasks
│   └── tasks.py                # sample @task
├── templates/
│   ├── base.html
│   └── _analytics.html
├── manage.py
├── pyproject.toml
├── setup.cfg                   # django-migration-linter exclude_apps
├── .env.example
└── .env (gitignored)
```

## Key commands

```sh
cp .env.example .env          # then set a real DJANGO_SECRET_KEY
createdb silk_db
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open <http://127.0.0.1:8000/admin/> and sign in with the new superuser.

Run the task worker in a second terminal (shares the venv and DB with `runserver`):

```sh
uv run manage.py db_worker
```

| Task | Command |
| --- | --- |
| Install deps | `uv sync` |
| Dev server | `uv run manage.py runserver` |
| Task worker | `uv run manage.py db_worker` |
| Migrate | `uv run manage.py migrate` |
| Make migrations | `uv run manage.py makemigrations` |
| Shell (IPython, models auto-imported) | `uv run manage.py shell_plus` |
| Superuser | `uv run manage.py createsuperuser` |
| Test | `uv run pytest` |
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format .` |
| List URLs | `uv run manage.py show_urls` |
| Lint migrations | `uv run manage.py lintmigrations` |
| Clear Silk log | `uv run manage.py silk_clear_request_log` |

## Profiling with Silk

Dev-only, mounted at `/silk/` when `DEBUG=True`. Every request middleware-profiles automatically; wrap a specific function with `@silk_profile(name="...")` for finer-grained timing (see `references/dev-tools.md` for the prod-safe no-op pattern — don't decorate app code unconditionally, it crashes outside `DEBUG`).

## Background tasks

`jobs/tasks.py` defines `send_welcome_email`, enqueued with:

```python
from jobs.tasks import send_welcome_email
send_welcome_email.enqueue("someone@example.com")
```

The `db_worker` management command picks it up from the `django_tasks_database` tables — no broker required.

## Environment variables

See `.env.example` for the full list.

---

Built with [Seedkit](https://github.com/RobustaRush/seedkit).
