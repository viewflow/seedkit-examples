## Prompt

```
/seedkit

Project name: 05-orbit-demo
Purpose: scratch project to exercise django-orbit and verify outbound mail flows are captured.

Settings layout: single file.
Database: SQLite.
Lint with Ruff: yes.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: no.
Task runner: none.
Add-ons:
  - debug: django-orbit (observability dashboard + MCP)
  - email: console backend in local, plus Mailpit running in Docker for richer inspection
  - HTML email base template + `send_test_email` command: yes. Also `uv run manage.py startapp mailer`, register `mailer` in `INSTALLED_APPS`, and put the command under `mailer/management/commands/`.
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: yes.
  - robots.txt: no.
  - django-extensions: no.
  - Devcontainer: no.
Run the foundation + boot check. Spin up Mailpit via a one-service `docker-compose.yml`, point Django at SMTP `localhost:1025`, send the test mail with `manage.py send_test_email`, and confirm it appears in Mailpit's UI on `:8025`.
```

---

# 05-orbit-demo

Scratch project to exercise django-orbit and verify outbound mail flows are captured.

## Stack

- Django 6, single-file settings (`config/settings.py`), SQLite.
- Lint: Ruff.
- Test runner: stock `manage.py test`.
- No i18n, no custom user model, no auth add-on, no structured logging, no task runner.
- Debug: [django-orbit](https://github.com/kmmbvnr/django-orbit) — observability dashboard at `/orbit/` (dev-only).
- Email: console backend, `smtp://localhost:1025` when Mailpit is running (`docker-compose.yml`, UI at `:8025`).
- `mailer` app: HTML email base template (`templates/email/base.html`) + `send_test_email` command.
- Health checks: `/healthz` (liveness), `/readyz` (readiness).

## Setup

```sh
cp .env.example .env   # then set DJANGO_SECRET_KEY
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

```sh
docker compose up -d mailpit   # SMTP :1025, web UI :8025
uv run manage.py runserver
```

Visit `/admin/`, `/orbit/`, and Mailpit's UI at <http://localhost:8025>.

## Send a test email

```sh
uv run manage.py send_test_email you@example.com
```

With Mailpit running, inspect the rendered HTML at <http://localhost:8025>.

## Commands

```sh
uv run manage.py test      # test
uv run ruff check .        # lint
uv run ruff format .       # format
```

Built with [Seedkit](https://github.com/viewflow/seedkit).
