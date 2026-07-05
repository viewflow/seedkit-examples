# 06-silk-lab

- Settings layout: split (`config/settings/{base,local,production,test}.py`).
- Database: PostgreSQL, host Postgres (not Docker). Dev DB name `silk_db`.
- Request handling: WSGI.
- Custom user model: none. Auth: none.
- Cache: Django's default (`LocMemCache`).
- Background tasks: Django Tasks (`django.tasks` API surface) backed by `django-tasks-db` (`TASKS["default"]["BACKEND"] = "django_tasks_db.DatabaseBackend"`). The installed `django-tasks-db` 0.12.0 still targets the standalone `django-tasks` backport package rather than Django 6's built-in `django.tasks` module — use `from django_tasks import task`, not `from django.tasks import task`. `jobs` app: `apps.py::ready()` imports `tasks` to register them; `jobs/tasks.py` has a sample `send_welcome_email` task. Run the worker with `manage.py db_worker`.
- Debug toolbar: `django-silk` at `/silk/`, DEBUG-gated in `config/settings/local.py`.
- Database safety (all DEBUG-gated in `local.py`): `django-zeal` (N+1 detection, `ZEAL_RAISE_ON_VIOLATION = True`), `django-migration-linter` (`manage.py lintmigrations`, exclusions in `setup.cfg`), `django-test-migrations` (`migrator` pytest fixture, no wiring needed beyond the dependency).
- `django-extensions`: yes, `local.py` only.
- Email: console backend in dev (`EMAIL_URL=consolemail://`), gated fail-fast in production via `env.NOTSET`. No HTML email base template.
- Analytics: GoatCounter, `ANALYTICS_ID` / `ANALYTICS_HOST` via `config/context_processors.py::analytics`, snippet in `templates/_analytics.html`, gated on `not DEBUG`.
- Health checks: `config/views.py::liveness` (`/healthz`) and `::readiness` (`/readyz`, checks DB).
- Lint: Ruff (`pyproject.toml`). Tests: pytest + pytest-django (`DJANGO_SETTINGS_MODULE=config.settings.test`). No type checking, no pre-commit hooks, no i18n, no CI, no production deploy target (skipped by request).
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
cp .env.example .env
createdb silk_db
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
uv run manage.py db_worker       # second terminal
uv run pytest
uv run ruff check .
uv run manage.py lintmigrations
```
