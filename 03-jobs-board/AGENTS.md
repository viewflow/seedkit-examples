# 03 Jobs Board — agent context

## Stack decisions

- Settings: single file, `config/settings.py` (not split base/local/production).
- Database: PostgreSQL, running in Docker (`docker-compose.yml`, service `db`).
- Request handling: WSGI (`config.wsgi`).
- Dev loop: `manage.py` runs inside the `web` container via `docker compose exec`, not on the host. Use `python`, not `uv run`, for any command inside a container.
- Custom user model: no — `AUTH_USER_MODEL` is `mailauth_user.EmailUser`, shipped by `django-mail-auth`'s `mailauth.contrib.user` (registered via `config.apps.MailAuthUserConfig`, pinned to `AutoField` to match the package's own migrations).
- Auth: `django-mail-auth` — passwordless magic-link. `mailauth.contrib.admin` overrides the admin login too.
- i18n: yes — `LocaleMiddleware`, `LANGUAGES`, `LOCALE_PATHS` wired. English only; add languages to `LANGUAGES` and run `compilemessages`/`makemessages` inside `web`.
- Background tasks: Celery + Celery Beat. Broker `REDIS_URL/1`, result backend `REDIS_URL/2`. `jobs` app holds `tasks.py`; `celery_app.autodiscover_tasks()` only scans `INSTALLED_APPS`.
- Email: console backend in dev (`EMAIL_URL=consolemail://`).
- Health checks: `/healthz` (liveness, no external checks), `/readyz` (readiness, checks DB via `SELECT 1`).
- Test runner: stock `manage.py test`.
- Lint / type check / pre-commit / devcontainer / CORS / REST API / frontend / robots.txt / django-extensions: none.
- Task runner: `just` (`justfile`), container-loop bodies (`docker compose exec -T web ...`).
- Production/deploy: skipped — only the `dev` build stage exists in `Dockerfile`, no prod Dockerfile stage or deploy compose file.

## Project layout

```
03-jobs-board/
├── config/
│   ├── settings.py       # single-file settings; env-driven via django-environ
│   ├── urls.py            # root redirect, admin, mailauth, healthz/readyz
│   ├── views.py            # liveness / readiness views
│   ├── celery.py           # Celery app, autodiscover_tasks()
│   ├── apps.py             # MailAuthUserConfig (pins AutoField)
│   ├── wsgi.py / asgi.py
│   └── __init__.py         # exports celery_app
├── jobs/
│   └── tasks.py             # @shared_task send_daily_digest; CELERY_BEAT_SCHEDULE entry
├── templates/
│   ├── base.html
│   └── registration/        # login.html, login_requested.html, logged_out.html (mailauth)
├── docker-compose.yml        # db, redis, web, worker, beat — only web publishes a host port
├── Dockerfile                 # single `dev` stage (uv builder image)
├── justfile
├── .env / .env.example
└── manage.py
```

## Key commands

```sh
just install     # docker compose build
just dev         # docker compose up (web + worker + beat + db + redis)
just migrate      # docker compose exec -T web python manage.py migrate
just makemigrations
just test          # docker compose exec -T web python manage.py test
just shell
just superuser
```

Fallback: `docker compose exec -T web python manage.py <command>` (add `-t`/drop `-T` for `shell`/`createsuperuser`, which need a TTY).
