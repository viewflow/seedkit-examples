# 09-ssh-deploy — agent context

## Stack decisions

- Settings layout: split (`config/settings/{base,local,production,test}.py`).
- Database: PostgreSQL, Postgres-in-Docker for local dev (`docker-compose.yml`, `db` service).
- Request handling: WSGI.
- Custom user model: no — stock `django.contrib.auth.User`.
- Lint: Ruff (`pyproject.toml` `[tool.ruff]`).
- Tests: pytest + pytest-django (`pyproject.toml` `[tool.pytest.ini_options]`, settings module `config.settings.test`).
- Type checking: none.
- Pre-commit hooks: none.
- i18n: none.
- Auth add-on: none — stock Django auth, admin login only.
- Structured logging: `structlog` + `django-structlog`, pretty console in dev / JSON in prod, request-scoped `request_id`.
- Task runner: mise (`mise.toml`).
- Redis: `django-redis` cache backend, `/0`.
- Background tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`), app `jobs`, worker command `rqworker default`, queue on Redis `/3`.
- Analytics: Umami (self-hosted), env-driven `ANALYTICS_ID` / `ANALYTICS_HOST`.
- Email: none — this project sends no transactional mail; Django's default backend is untouched, `test.py` still forces `locmem` for test isolation.
- CORS: none. REST API: none. Frontend: none (minimal `templates/base.html` exists only so the analytics include resolves).
- Health checks: yes — `/healthz` (liveness), `/readyz` (DB readiness), wired into the Caddy healthcheck and the container `HEALTHCHECK`.
- `robots.txt`: none. `django-extensions`: none. Devcontainer: none.
- Security: Django deploy security settings (`config/settings/production.py`) + CSP via `django-csp`.
- Error reporting: Bugsink (self-hosted, Sentry protocol), PII scrubbed (`Authorization`/`Cookie` headers dropped, `send_default_pii=False`).
- GDPR: user data export/delete management commands under `jobs/management/commands/`.
- CI: GitHub Actions test workflow (`.github/workflows/test.yml`), Postgres + Redis services.
- Deploy: GitHub Actions via SSH (`.github/workflows/deploy.yml`) — builds + pushes a GHCR image, then SSHes into the host to `docker compose pull && migrate && up -d`. Built on `deploy/docker-compose.prod.yml` + `deploy/Caddyfile` + `deploy/.env.prod.example`.
- Database backups: `django-dbbackup` to S3-compatible storage (production only, wrapped in `if not DEBUG:`).
- Production Dockerfile: multi-stage — `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` builder → `python:3.12-slim-bookworm` runtime. `postgresql-client-17` is installed via the PGDG apt repo (Bookworm's default repo only ships major 15, which doesn't match the `postgres:17` server).

## Layout

```
config/
  settings/
    base.py         # env-driven core, INSTALLED_APPS, logging, redis, tasks
    local.py        # dev delta (none — base.py already dev-safe)
    production.py   # security, CSP, Bugsink, dbbackup
    test.py         # locmem cache/email, immediate task backend
  urls.py           # admin, django-rq, healthz/readyz
  views.py          # liveness/readiness views
  context_processors.py   # analytics context
  wsgi.py / asgi.py        # -> config.settings.production
jobs/                # only registered app — home of tasks.py + GDPR commands
  tasks.py           # sample @task
  management/commands/{export,delete}_user_data.py
templates/
  base.html          # minimal base template (frontend: none)
  _analytics.html    # Umami snippet
deploy/
  docker-compose.prod.yml   # web, worker, db, redis, caddy, bugsink, umami
  Caddyfile
  .env.prod.example
Dockerfile           # multi-stage build, target `prod`
docker-compose.yml   # local db + redis only
mise.toml
.github/workflows/{test,deploy}.yml
```

## Key commands

```sh
cp .env.example .env
docker compose up -d
mise run install
mise run migrate
mise run superuser
mise run dev        # second terminal: mise run worker
mise run test
mise run lint
```

Deploy: push to `main` (needs `SSH_HOST` / `SSH_USER` / `SSH_KEY` / `GHCR_TOKEN` repo secrets). See `README.md` `## Deploy` for the first-time server setup and rollback commands.
