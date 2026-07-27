# 01-minimal-blog

A tiny Django blog used to verify the scaffolding skill works end-to-end.

## Stack

- Django 6.0, Python 3.12, managed with `uv`.
- SQLite database (`db.sqlite3`, gitignored).
- Single settings file: `config/settings.py`, configured via `django-environ`
  reading `.env` (see `.env.example`).
- Vanilla `django.contrib.auth`, no custom user model.
- Email: console backend, controlled by `EMAIL_URL` (defaults to
  `consolemail://`).
- No i18n, no REST framework, no frontend build, no task runner.

## Layout

- `blog/` — the only app: a `Post` model with list/detail views under
  `templates/blog/`.
- `templates/base.html` — shared base template.
- `config/` — project settings, root urlconf, WSGI/ASGI entrypoints.

## Commands

```sh
uv run manage.py migrate
uv run manage.py runserver
uv run manage.py test
```

## Conventions

- Keep this project minimal — it's a smoke-test fixture, not a product.
  Don't add apps, dependencies, or settings beyond what's needed to prove the
  scaffold boots and admin login works.
