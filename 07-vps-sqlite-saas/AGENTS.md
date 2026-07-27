# 07-vps-sqlite-saas

## Stack decisions

- Django 6, split settings layout: `config/settings/{base,local,production,test}.py`
- Database: SQLite (`db.sqlite3` dev, `/data/site.sqlite3` prod). WAL + IMMEDIATE pragmas applied in `production.py`.
- Request handling: WSGI
- Custom user model: `users.User` (extends `AbstractUser`, email as `USERNAME_FIELD`, no `username`)
- Ruff: lint + format (`pyproject.toml` `[tool.ruff]`)
- Test runner: pytest + pytest-django (`config.settings.test`)
- Type checking: pyright + django-stubs (`pyproject.toml` `[tool.pyright]`)
- Pre-commit: ruff-check, ruff-format, pyright, trailing-whitespace/EOF/yaml/toml checks (`.pre-commit-config.yaml`)
- i18n: not enabled
- Cache: SQLite (`cache.sqlite3` dev / `/data/cache.sqlite3` prod), `DatabaseCache` + `config.routers.CacheRouter`
- Background tasks: Django Tasks, database backend (`django-tasks-db`) — `jobs` app, `jobs/tasks.py` has `log_greeting`
- Static: WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware`, `CompressedManifestStaticFilesStorage` in prod)
- Media: local filesystem, served by Caddy from a shared Docker volume on the VPS
- Email: SMTP in production (`EMAIL_URL`, Postmark placeholder), console backend in local
- Auth: django-allauth (email login, `ACCOUNT_EMAIL_VERIFICATION="mandatory"` in prod) + django-axes (lockout) + `allauth.mfa` (TOTP 2FA)
- Structured logging: structlog + django-structlog, JSON in prod / console in dev, request-scoped `request_id`
- Task runner: mise (`mise.toml`)
- Security: HSTS, secure cookies, SSL redirect, CSRF trusted origins (`config/settings/production.py`)
- CSP: django-csp (`production.py` only)
- Error reporting: Sentry (`sentry-sdk`, gated on `SENTRY_DSN`)
- CI: GitHub Actions (`.github/workflows/test.yml`)
- Deploy: VPS via Docker + Caddy (`Dockerfile`, `deploy/docker-compose.prod.yml`, `deploy/Caddyfile`)
- Backups: Litestream → S3-compatible storage (`litestream.yml`, `entrypoint.sh`); no django-dbbackup

## Layout

```
config/
  settings/
    base.py         # shared settings, env-driven
    local.py         # dev delta (empty — base covers it)
    production.py     # security, CSP, Sentry, WhiteNoise, SQLite WAL pragmas
    test.py          # fast/deterministic test overrides
  routers.py         # CacheRouter — routes django_cache app to the `cache` DB
  urls.py
  views.py           # liveness / readiness probes
  wsgi.py / asgi.py
users/               # custom user model (AUTH_USER_MODEL)
jobs/                # django-tasks-db tasks app
Dockerfile           # multi-stage: uv builder -> slim runtime + Litestream
litestream.yml        # DB replication config (baked into image)
entrypoint.sh         # restore -> migrate -> createcachetable -> litestream replicate -exec gunicorn
deploy/
  docker-compose.prod.yml
  Caddyfile
  .env.prod.example
.github/workflows/test.yml
mise.toml
```

## Key commands

```sh
mise trust && mise install
mise run install       # uv sync
mise run dev            # runserver
mise run migrate
mise run makemigrations
mise run shell
mise run superuser
mise run test           # pytest
mise run lint           # ruff check
mise run fmt             # ruff format
mise run typecheck       # pyright
mise run collectstatic
mise run worker          # python manage.py db_worker
mise run deploy          # docker compose -f deploy/docker-compose.prod.yml up -d
```

Fallback without mise: `uv run manage.py <command>`.
