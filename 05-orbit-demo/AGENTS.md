# 05-orbit-demo

Django 6 scratch project. Stack decisions:

- Settings: single file (`config/settings.py`), env-driven via `django-environ`.
- Database: SQLite (`db.sqlite3`), WAL + IMMEDIATE pragmas applied when `DEBUG=False`.
- Request handling: WSGI.
- Custom user model: no.
- Auth: none.
- Lint: Ruff (`DJ`/`S`/`SIM`/`RUF` rulesets enabled).
- Test runner: stock `manage.py test`.
- Debug toolbar: `django-orbit` at `/orbit/`, dev-only (`if DEBUG`), with MCP support (`orbit_mcp` command).
- Email: `django-environ` `EMAIL_URL`. Dev default is `consolemail://`; `.env` points at Mailpit (`smtp://localhost:1025`) so this project's mail flows are inspectable.
- HTML email: `templates/email/base.html` (table layout, inline styles) + `mailer/management/commands/send_test_email.py`.
- Health checks: `/healthz` (liveness), `/readyz` (readiness) in `config/views.py`.
- i18n, CORS, REST API, frontend, GDPR, CI, deploy target: not applied.

## Layout

```
05-orbit-demo/
├── config/
│   ├── settings.py       # single-file settings
│   ├── urls.py           # root redirect, admin, healthz/readyz, orbit/ (DEBUG)
│   ├── views.py          # liveness/readiness views
│   ├── wsgi.py
│   └── asgi.py
├── mailer/
│   └── management/commands/send_test_email.py
├── templates/email/
│   ├── base.html
│   └── test.html
├── docker-compose.yml    # mailpit (local SMTP + web UI on :8025)
├── manage.py
├── pyproject.toml
└── .env.example
```

## Key commands

```sh
cp .env.example .env               # then set a real DJANGO_SECRET_KEY
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
uv run manage.py test
uv run ruff check .
uv run ruff format .
docker compose up -d mailpit       # local SMTP capture — http://localhost:8025
uv run manage.py send_test_email you@example.com
```
