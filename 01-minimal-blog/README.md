## Prompt

```
/seedkit

Project name: 01-minimal-blog
Purpose: a tiny blog to verify the skill works end-to-end.

Settings layout: single file (`config/settings.py`).
Database: SQLite.
Lint with Ruff: no.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none (vanilla `django.contrib.auth`).
Structured logging: no.
Task runner: none.
Add-ons:
  - email: console backend (`EMAIL_URL=consolemail://`).
  - HTML email base template: no.
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: no (this case is the bare floor — no extra views).
  - robots.txt: no.
  - django-extensions: no.
  - Devcontainer: no.

Production setup: skip.

Run the foundation, the boot check (migrate + createsuperuser), and confirm /admin/ login works.
```

---

# 01-minimal-blog

A tiny blog to verify the skill works end-to-end.

## Stack

- Django 6, single-file settings (`config/settings.py`)
- SQLite (dev default, no `DATABASE_URL` needed)
- `django-environ` for env-driven settings
- WSGI (stock `runserver` / gunicorn-compatible)
- Email: console backend (`EMAIL_URL=consolemail://`)
- Vanilla `django.contrib.auth`, no auth add-on
- Test runner: stock `manage.py test`

## Setup

```sh
cp .env.example .env   # then set a real DJANGO_SECRET_KEY
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Open <http://127.0.0.1:8000/admin/> and sign in.

## Key commands

```sh
uv run manage.py migrate
uv run manage.py test
uv run manage.py runserver
```

Built with [Seedkit](https://github.com/viewflow/seedkit).
