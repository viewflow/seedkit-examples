# orbit-demo

Scratch project to exercise [django-orbit](https://github.com/astro-stack/django-orbit)
(observability dashboard + MCP server) and verify outbound mail flows are
captured via [Mailpit](https://mailpit.axllent.org/).

## Setup

```sh
uv sync
docker compose up -d mailpit
uv run manage.py migrate
uv run manage.py runserver
```

- App: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- Orbit dashboard: http://localhost:8000/orbit/
- Mailpit UI: http://localhost:8025/
- Health checks: http://localhost:8000/healthz, http://localhost:8000/readyz

## Email

By default `EMAIL_BACKEND` points at Mailpit's SMTP listener
(`localhost:1025`), so every email sent by the app shows up in the Mailpit
UI. To print mail to the console instead (e.g. when Mailpit isn't running),
set:

```sh
export DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Send a test email (text + HTML alternative) to confirm delivery:

```sh
uv run manage.py send_test_email to@example.com
```

## Lint

```sh
uv run ruff check .
```
