# 09-ssh-deploy

- Settings layout: split (`config/settings/{base,local,production,test}.py`).
- Database: PostgreSQL, Postgres-in-Docker for local dev (`docker-compose.yml`; remapped to host port 5435 — 5432 is taken by a native Postgres on this dev machine).
- Request handling: WSGI.
- Custom user model: none.
- Auth: none.
- Cache: Redis (`django-redis`), `REDIS_URL` /0.
- Background tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq` + `django-rq`, `REDIS_URL` /3). Tasks live in `jobs/tasks.py`, registered via `jobs/apps.py::ready()`.
- Logging: `structlog` + `django-structlog` — pretty console in dev, JSON in prod, per-request `request_id` via `RequestMiddleware`.
- Analytics: Umami (self-hosted), env-driven `ANALYTICS_ID` / `ANALYTICS_HOST`, wired through `config/context_processors.py` + `templates/_analytics.html`.
- Email: none — no `EMAIL_BACKEND` override, test settings use the locmem backend.
- Health checks: `/healthz` (liveness), `/readyz` (DB reachable) — `config/views.py`.
- Security: Django's HSTS / secure-cookie / SSL-redirect settings + `django-csp` in `config/settings/production.py`.
- Error reporting: Bugsink (self-hosted, Sentry-protocol) via `sentry-sdk`, PII scrubbing (`send_default_pii=False` + header scrub) for GDPR.
- GDPR: `jobs/management/commands/{export_user_data,delete_user_data}.py` for user data requests.
- Database backups: `django-dbbackup` → S3-compatible bucket (`DBBACKUP_BUCKET`), wrapped in `if not DEBUG` in `production.py`.
- Lint: Ruff. Tests: pytest + pytest-django. No type checking. No pre-commit hooks. No i18n.
- Task runner: mise (`mise.toml`).
- CI: GitHub Actions test workflow (`.github/workflows/test.yml`) — Postgres + Redis services, ruff, `manage.py check --deploy`, pytest.
- Deploy: GitHub Actions over SSH (`.github/workflows/deploy.yml`) — builds + pushes a GHCR image, SSHes to the host to `pull && migrate && up -d`. Built on top of the VPS Docker + Caddy pattern (`deploy/docker-compose.prod.yml`, `deploy/Caddyfile`).
- Production Dockerfile: multi-stage — `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` builder → `python:3.12-slim-bookworm` runtime. Installs `postgresql-client-17` from the PGDG apt repo (Bookworm's stock package is v15, which mismatches the `postgres:17` service).

## Layout

```
09-ssh-deploy/
├── config/
│   ├── settings/{base,local,production,test}.py
│   ├── context_processors.py   # analytics
│   ├── urls.py
│   ├── views.py                 # healthz, readyz
│   ├── wsgi.py / asgi.py
├── jobs/
│   ├── apps.py                  # ready() imports tasks
│   ├── tasks.py                 # sample @task
│   ├── management/commands/{export_user_data,delete_user_data}.py
├── templates/
│   ├── base.html
│   └── _analytics.html
├── deploy/
│   ├── docker-compose.prod.yml   # web, worker, db, redis, bugsink, caddy
│   ├── Caddyfile
│   └── .env.prod.example
├── .github/workflows/{test,deploy}.yml
├── Dockerfile
├── docker-compose.yml            # local db + redis only
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
docker compose up -d           # db + redis
mise run migrate
mise run superuser
mise run dev                    # runserver
mise run worker                 # rqworker default, in a second terminal
mise run test
mise run lint
mise run fmt
mise run deploy                  # deploy-migrate then docker compose up -d, see deploy/
```

Fallback without mise: `uv run manage.py <command>` for every task above.
