# 03-jobs-board — agent context

Job board with background email notifications and a daily digest.

## Stack decisions

- Settings: single file, `config/settings.py`, env-driven via `django-environ`.
- Database: PostgreSQL, Postgres in Docker (`docker-compose.yml`, service `db`).
  Host published port is **5433** (not the default 5432 — that port was already
  taken by a native Postgres on the scaffolding machine); `redis` published on
  **6380** for the same reason (default 6379 taken). Adjust `docker-compose.yml`
  + `.env` `DATABASE_URL` / `REDIS_URL` if your machine is clear of those ports.
- Custom user model: no. Auth = `django-mail-auth`'s `mailauth.contrib.user.EmailUser`
  (`AUTH_USER_MODEL = "mailauth_user.EmailUser"`) — no password column.
- Auth: `django-mail-auth` (passwordless magic-link). `mailauth.contrib.admin` before
  `django.contrib.admin` in `INSTALLED_APPS` so `/admin/` also uses magic-link login.
- Background tasks: Celery + Celery Beat, broker/results on Redis DB `/1` and `/2`.
- Cache: `django-redis`, Redis DB `/0`.
- Email: console backend in dev (`EMAIL_URL=consolemail://`).
- i18n: yes — `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS`; ships with `en` only,
  no language-prefixed URLs (Pattern A — header/cookie detection).
- Health checks: `/healthz`, `/readyz` in `config/views.py`.
- Task runner: `just` (`justfile`).
- Test runner: stock `manage.py test`.
- No: Ruff, pyright/django-stubs, pre-commit, devcontainer, CORS, REST API,
  frontend, robots.txt, django-extensions, structured logging, production deploy.

## Layout

```
03-jobs-board/
├── config/
│   ├── settings.py       # single-file settings, env-driven
│   ├── urls.py            # admin, mailauth, i18n, healthz/readyz
│   ├── celery.py          # Celery app, autodiscover_tasks()
│   ├── views.py           # liveness / readiness views
│   ├── wsgi.py / asgi.py
│   └── __init__.py        # exposes celery_app
├── jobs/                  # domain app — registered in INSTALLED_APPS
│   └── tasks.py           # @shared_task send_daily_digest + CELERY_BEAT_SCHEDULE
├── templates/
│   ├── base.html
│   └── registration/      # mailauth login / login_requested / logged_out
├── docker-compose.yml      # db (Postgres 17) + redis, local only
├── justfile
├── .env.example / .env
└── manage.py
```

## Key commands

```sh
docker compose up -d
just install
just migrate
just superuser
just dev            # runserver
just worker         # celery worker
just beat           # celery beat
just test
```

Fallback without `just`: `uv run manage.py <command>`.
