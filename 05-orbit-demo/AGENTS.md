# 05-orbit-demo

Scratch project to exercise django-orbit and verify outbound mail flows are captured.

## Stack decisions

- Settings layout: single file (`config/settings.py`).
- Database: SQLite (`db.sqlite3`, dev default via `DATABASE_URL`).
- Request handling: WSGI.
- Lint: Ruff (`E W F I UP B DJ S SIM RUF`).
- Test runner: stock `manage.py test`.
- Type checking: none.
- Pre-commit hooks: none.
- i18n: none.
- Custom user model: none.
- Auth: none.
- Structured logging: none (stock `logging`, console handler; orbit handler appended in DEBUG).
- Task runner (mise/just/make): none.
- Debug: django-orbit — dashboard at `/orbit/`, DEBUG-gated `INSTALLED_APPS` + middleware + logging handler.
- Email: `django-environ` `EMAIL_URL` — `consolemail://` default in DEBUG; `.env` points at Mailpit (`smtp://localhost:1025`). Mailpit runs via `docker-compose.yml` (web UI `:8025`).
- `mailer` app: HTML email base template (`templates/email/base.html`) + `send_test_email` management command under `mailer/management/commands/`.
- Health checks: `/healthz`, `/readyz` in `config/views.py` + `config/urls.py`.
- CORS: none. REST API: none. Frontend: none. robots.txt: none. django-extensions: none. Devcontainer: none.

## Layout

```
config/
  settings.py       # single-file settings
  urls.py           # root redirect, healthz/readyz, orbit (DEBUG)
  views.py          # liveness/readiness views
mailer/
  management/commands/send_test_email.py
templates/
  email/base.html
  email/test.html
docker-compose.yml   # mailpit only
```

## Key commands

```sh
cp .env.example .env
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
docker compose up -d mailpit
uv run manage.py runserver
uv run manage.py send_test_email you@example.com
uv run manage.py test
uv run ruff check .
uv run ruff format .
```
