# 07-vps-sqlite-saas

- Settings layout: split (`config/settings/{base,local,production,test}.py`).
- Database: SQLite (`db.sqlite3` in dev, `/data/site.sqlite3` on the VPS). WAL + IMMEDIATE pragmas applied in `production.py`.
- Request handling: WSGI.
- Custom user model: `users.User` (email as `USERNAME_FIELD`, no `username`, extends `AbstractUser`).
- Auth: `django-allauth` (email login, mandatory verification in production) + `django-axes` (brute-force lockout) + `allauth.mfa` (TOTP + recovery codes, forced in production).
- Cache: separate SQLite DB (`cache.sqlite3`), routed via `config/routers.py::CacheRouter` + `django.core.cache.backends.db.DatabaseCache`.
- Background tasks: Django Tasks + `django-tasks-db` (database backend, no broker). `jobs` app — `jobs/apps.py::ready()` imports `jobs/tasks.py` to register `@task`-decorated functions. Worker: `manage.py db_worker`.
- Storage: WhiteNoise for static files (compressed, manifest-hashed in production). Media on a Docker named volume, served by Caddy on the VPS (no S3).
- Email: SMTP in production (`EMAIL_URL`, Postmark placeholder), console backend in local. `DEFAULT_FROM_EMAIL` / `SERVER_EMAIL` / `DJANGO_ADMINS` wired.
- Logging: `structlog` — `ConsoleRenderer` in dev, `JSONRenderer` in prod, `django_structlog` middleware binds `request_id` / `user_id` per request.
- Health checks: `/healthz` (liveness), `/readyz` (DB reachable) — `config/views.py`.
- Security: Django's HSTS / secure-cookie / SSL-redirect settings in `config/settings/production.py` + `django-csp` (enforced, not report-only).
- Error tracking: Sentry SaaS (`sentry-sdk`, `SENTRY_DSN` env var, production-only).
- Lint: Ruff. Types: pyright + django-stubs. Tests: pytest + pytest-django. Pre-commit hooks wired (ruff-check, ruff-format, pyright, plus stock hygiene hooks). No i18n.
- Task runner: mise (`mise.toml`).
- CI: GitHub Actions (`.github/workflows/test.yml`) — ruff, pyright, `manage.py check --deploy --fail-level WARNING`, pytest. SQLite-only, no service containers.
- Backups: Litestream — streams `site.sqlite3` and `cache.sqlite3` WAL frames to S3-compatible storage. No `django-dbbackup`.
- Deploy: VPS via Docker + Caddy. Multi-stage `Dockerfile` (`uv` builder on `python:3.13-trixie-slim` → `python:3.13-slim-trixie` runtime with the Litestream `.deb` baked in). `entrypoint.sh` restores from S3 (no-op if no replica yet), runs `migrate --noinput` + `createcachetable`, then execs gunicorn under `litestream replicate`. No `db` service in `deploy/docker-compose.prod.yml` — SQLite lives on the shared `data` named volume between `web` and `worker`.
- GDPR: out of scope for this project.

## Layout

```
07-vps-sqlite-saas/
├── config/
│   ├── settings/{base,local,production,test}.py
│   ├── routers.py           # CacheRouter
│   ├── urls.py
│   ├── views.py              # healthz, readyz
│   └── wsgi.py / asgi.py
├── jobs/                     # django-tasks-db: apps.py ready() + tasks.py
├── users/                    # custom User model (email login) + admin
├── deploy/
│   ├── docker-compose.prod.yml
│   └── Caddyfile
├── Dockerfile
├── entrypoint.sh              # litestream restore → migrate → litestream replicate -exec gunicorn
├── litestream.yml
├── manage.py
├── mise.toml
├── pyproject.toml
├── .env.example
└── .env (gitignored)
```

## Key commands

```sh
cp .env.example .env          # then set a real DJANGO_SECRET_KEY
mise trust && mise install
mise run install
mise run migrate
uv run manage.py createcachetable --database cache
mise run superuser
mise run dev
mise run test
mise run lint
mise run typecheck
mise run worker                 # uv run manage.py db_worker
mise run deploy                 # docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d, see deploy/
```

Fallback without mise: `uv run manage.py <command>` for every task above.
