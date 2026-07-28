# 05-orbit-demo

Scratch Django project to exercise [django-orbit](https://github.com/astro-stack/django-orbit)
and verify outbound mail flows are captured.

## Stack

- Django (single-file settings in `config/settings.py`), SQLite
- [django-orbit](https://github.com/astro-stack/django-orbit) observability dashboard at `/orbit/`
- Mailpit (Docker) for outbound-mail inspection, UI on <http://localhost:8025>
- Ruff for linting, stock `manage.py test` for tests

## Quick start

```sh
uv sync
docker compose up -d mailpit
uv run manage.py migrate
uv run manage.py runserver
```

Then:

- <http://127.0.0.1:8000/orbit/> — Orbit dashboard
- <http://127.0.0.1:8000/healthz> — liveness (`ok`)
- <http://127.0.0.1:8000/readyz> — readiness (`ready`, checks the database)
- <http://localhost:8025/> — Mailpit UI

## Email

Mail goes to Mailpit over SMTP (`localhost:1025`) by default. Set
`EMAIL_MODE=console` to print messages to stdout instead.

Send a test message (text + HTML alternative):

```sh
uv run manage.py send_test_email to@example.com
```

It should appear in the Mailpit UI and in Orbit's mail watcher.

## Development

```sh
uv run ruff check .
uv run manage.py test
```
