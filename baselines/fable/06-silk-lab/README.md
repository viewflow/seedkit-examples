# silk-lab

Django playground for profiling request paths with [django-silk](https://github.com/jazzband/django-silk)
and running background email tasks on the Django Tasks database backend.

## Setup

```sh
createdb silk_db
cp .env.example .env
uv sync
uv run manage.py migrate
```

## Run

```sh
uv run manage.py runserver          # terminal 1
uv run manage.py db_worker          # terminal 2 — processes queued tasks
```

Enqueue the sample task:

```sh
uv run manage.py shell -c "from jobs.tasks import send_welcome_email; send_welcome_email.enqueue('you@example.com')"
```

The worker picks it up and the email prints to its console (`EMAIL_URL=consolemail://`).

- Profiling UI: <http://127.0.0.1:8000/silk/> — every request is recorded;
  `@silk_profile` blocks (see `config/views.py`) show under Profiling.
- Health checks: `/healthz` (liveness), `/readyz` (readiness, checks the DB).

## Tooling

```sh
uv run ruff check .              # lint
uv run pytest                    # tests (pytest-django; django-test-migrations available)
uv run manage.py lintmigrations  # django-migration-linter (project apps only)
uv run manage.py show_urls       # django-extensions
```

django-zeal logs N+1 query warnings in local development (`ZEAL_RAISE = False`).

Analytics: set `GOATCOUNTER_URL` in `.env` to your self-hosted GoatCounter base URL
to enable the tracking snippet in `templates/base.html`.
