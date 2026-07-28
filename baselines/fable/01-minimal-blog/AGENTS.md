# 01-minimal-blog

A tiny Django blog used to verify the project scaffold end-to-end.

## Stack

- Python 3.13, Django 6, managed with [uv](https://docs.astral.sh/uv/).
- Single settings file: `config/settings.py`, configured via environment
  variables (django-environ, `.env` for local development).
- SQLite database (`db.sqlite3` in the project root).
- Email goes to the console (`EMAIL_URL=consolemail://`).
- No REST API, no frontend pipeline, no custom user model — vanilla
  `django.contrib.auth` with the stock admin.

## Layout

- `config/` — project settings, urls, wsgi/asgi.
- `blog/` — the only app; `Post` model registered in the admin.

## Common commands

```sh
uv sync                        # install dependencies
uv run manage.py migrate       # apply migrations
uv run manage.py createsuperuser
uv run manage.py runserver     # http://127.0.0.1:8000/admin/
uv run manage.py test          # run the test suite (stock Django runner)
```

## Conventions

- All code changes must keep `uv run manage.py test` passing.
- New apps go in the project root and are added to `INSTALLED_APPS` in
  `config/settings.py`.
- Configuration belongs in environment variables, not hardcoded in settings;
  add new keys to `.env.example`.
