# 03-jobs-board

Job board with background email notifications and a daily digest.

## Stack decisions

- Settings: single file (`config/settings.py`), `django-environ`.
- Database: PostgreSQL in Docker (`docker-compose.yml`, `127.0.0.1:5432`).
- Request handling: WSGI.
- Custom user model: no — using `mailauth.contrib.user.EmailUser`.
- Auth: `django-mail-auth` (passwordless magic-link, `mailauth.contrib.admin` for admin login).
- Cache: Redis (`django-redis`), `docker-compose.yml` (`127.0.0.1:6379`).
- Background tasks: Celery + Celery Beat, Redis broker.
- Email: console backend in dev (`EMAIL_URL=consolemail://`).
- i18n: enabled (`LANGUAGES`, `LocaleMiddleware`, `LOCALE_PATHS`).
- Health checks: `/healthz`, `/readyz` in `config/views.py` / `config/urls.py`.
- Task runner: `just` (`justfile`).
- Tests: stock `manage.py test`.
- Lint / type check / pre-commit: none.
- Production setup: not applied (no Dockerfile, no deploy target).

## Layout

```
config/
  settings.py       # single-file settings
  urls.py           # root redirect, mailauth, healthz/readyz
  views.py          # liveness/readiness views
  celery.py         # Celery app, autodiscover_tasks()
  __init__.py       # exposes celery_app
jobs/
  tasks.py          # @shared_task: send_job_notification, send_daily_digest
templates/
  base.html
  registration/     # mailauth login/login_requested/logged_out
docker-compose.yml  # db (Postgres 17) + redis
justfile
.env.example
```

## Key commands

| Task | Command |
| --- | --- |
| `just install` | `uv sync` |
| `just dev` | `uv run manage.py runserver` |
| `just migrate` | `uv run manage.py migrate` |
| `just makemigrations` | `uv run manage.py makemigrations` |
| `just shell` | `uv run manage.py shell` |
| `just superuser` | `uv run manage.py createsuperuser` |
| `just test` | `uv run manage.py test` |
| `just worker` | `uv run celery -A config worker -l info` |
| `just beat` | `uv run celery -A config beat -l info` |

`docker compose up -d` starts `db` and `redis` before running any of the above.
