# 01-minimal-blog

- Settings layout: single `config/settings.py` (env-driven via `django-environ`).
- Database: SQLite, `db.sqlite3` at `BASE_DIR`.
- Request handling: WSGI.
- Custom user model: no (vanilla `django.contrib.auth`).
- Auth: none beyond stock `django.contrib.auth`.
- Email: console backend (`EMAIL_URL=consolemail://`).
- Lint / typecheck / pre-commit / i18n / structured logging / task runner: none.
- Test runner: stock `manage.py test`.

## Layout

```
01-minimal-blog/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── pyproject.toml
├── .env.example
└── .env (gitignored)
```

## Key commands

```sh
cp .env.example .env
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
uv run manage.py test
```
