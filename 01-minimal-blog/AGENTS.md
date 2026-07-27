# 01-minimal-blog

## Stack decisions

- Settings layout: single file (`config/settings.py`)
- Database: SQLite (dev default `db.sqlite3` at `BASE_DIR`, no `DATABASE_URL` set)
- Request handling: WSGI
- Custom user model: no (vanilla `django.contrib.auth.models.User`)
- Auth add-on: none
- Lint (Ruff): no
- Test runner: stock `manage.py test`
- Type checking: no
- Pre-commit hooks: no
- i18n: no
- Structured logging: no
- Task runner: none
- Email backend: console (`EMAIL_URL=consolemail://`)
- HTML email base template: no
- CORS: no
- REST API: none
- Frontend: none
- Health check endpoints: no
- robots.txt: no
- django-extensions: no
- Devcontainer: no
- Production setup: skipped

## Layout

```
01-minimal-blog/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── pyproject.toml
├── uv.lock
├── .env.example
└── .env (gitignored)
```

`/` redirects to `/admin/`. No domain app has been created yet — add one with
`uv run manage.py startapp <name>` and register it in `INSTALLED_APPS` before
adding `models.py` / `tasks.py` content.

## Key commands

```sh
uv run manage.py migrate
uv run manage.py test
uv run manage.py createsuperuser
uv run manage.py runserver
```
