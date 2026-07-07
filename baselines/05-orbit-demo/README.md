# 05-orbit-demo

Scratch project for exercising [django-orbit](https://github.com/astro-stack/django-orbit) and verifying outbound mail flows are captured.

## Setup

```bash
uv sync
uv run manage.py migrate
uv run manage.py runserver
```

- App: http://localhost:8000/
- Orbit dashboard: http://localhost:8000/orbit/
- Health check: http://localhost:8000/healthz/

## Mail

`EMAIL_BACKEND` defaults to the console backend. To route outbound mail through
Mailpit instead:

```bash
docker compose up -d                     # starts Mailpit (SMTP :1025, UI :8025)

DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
  uv run manage.py send_test_email --to demo@example.com
```

Then check:

- Mailpit UI: http://localhost:8025/
- Orbit dashboard's Mail entries: http://localhost:8000/orbit/ (mail is captured
  regardless of which `EMAIL_BACKEND` is active)

## Lint & tests

```bash
uv run ruff check .
uv run manage.py test
```
