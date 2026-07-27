# 06-silk-lab

Django 6 project. Profile a few request paths with django-silk and run a simple background email task on the DB backend.

## Stack decisions

- Settings layout: split (`config/settings/base.py`, `local.py`, `production.py`, `test.py`)
- Database: PostgreSQL, host-installed (`DATABASE_URL` in `.env`)
- Request handling: WSGI
- Custom user model: no
- Auth: none
- Lint: Ruff
- Test runner: pytest (`config.settings.test`)
- Type checking: no
- Pre-commit hooks: no
- i18n: no
- Structured logging: no
- Task runner (mise/just/make): none — use `uv run manage.py ...` directly
- Debug toolbar: django-silk (`/silk/`), dev-only, DEBUG-gated in `local.py`
- Background tasks: Django Tasks, Database backend (`django-tasks-db`) — `jobs` app, worker via `manage.py db_worker`
- Analytics: GoatCounter, env-driven (`ANALYTICS_ID` / `ANALYTICS_HOST`)
- Email: console backend in dev (`EMAIL_URL=consolemail://`)
- HTML email base template: no
- CORS: no
- REST API: none
- Frontend: none (minimal `templates/base.html` exists only so `_analytics.html` has somewhere to include)
- Devcontainer: no
- Health checks: `/healthz` (liveness), `/readyz` (DB readiness) in `config/views.py`
- `robots.txt`: no
- django-extensions: yes, dev-only, `local.py`
- Database safety: django-zeal, django-migration-linter, django-test-migrations — all dev-only
- Production setup (security settings, CSP, error reporting, GDPR, CI, deploy target, dbbackup): skipped

## Layout

```
config/
  settings/
    base.py        # env-driven core settings, shared by all
    local.py        # DEBUG-gated: silk, zeal, migration-linter, django-extensions
    production.py    # deltas from base (currently none — production setup was skipped)
    test.py          # fast test settings (locmem email/cache, immediate task backend)
  urls.py           # /, /admin/, /healthz, /readyz, /jobs/profile-demo/, /silk/ (DEBUG only)
  views.py          # liveness/readiness views
  context_processors.py  # analytics context processor
jobs/
  apps.py           # ready() imports tasks.py to register @task functions
  tasks.py          # send_welcome_email — sample Django Tasks task
  views.py          # profile_demo — @silk_profile usage example
templates/
  base.html         # minimal base template (frontend=none)
  _analytics.html   # GoatCounter snippet, gated on ANALYTICS_ID/ANALYTICS_HOST/DEBUG
setup.cfg           # django-migration-linter exclude_apps
```

## Key commands

```sh
createdb silk_db
uv run manage.py migrate
uv run manage.py runserver
uv run manage.py db_worker        # second terminal
uv run manage.py lintmigrations
uv run ruff check .
uv run ruff format .
uv run pytest
```
