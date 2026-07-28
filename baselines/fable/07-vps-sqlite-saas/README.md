# 07-vps-sqlite-saas

Production-ready SaaS skeleton for a single VPS: Django + SQLite (WAL) as the
"mini-prod" stack — no separate database, cache, or queue server — deployed with
docker-compose behind Caddy, with Litestream streaming the database to
S3-compatible storage.

## Stack

- **Django 6 / Python 3.14**, split settings (`config/settings/{base,local,production,test}.py`)
- **SQLite** everywhere: main DB (`db.sqlite3`), cache DB (`cache.sqlite3` +
  `DatabaseCache` + `CacheRouter`), and background tasks (Django Tasks with the
  `django-tasks-db` database backend, worker: `manage.py db_worker`)
- **Auth**: custom `users.User`, `django-allauth` (email login, mandatory
  verification, MFA/2FA), `django-axes` lockout
- **Ops**: structlog (JSON in prod, pretty in dev, request-scoped `request_id`),
  Sentry, WhiteNoise static, health endpoints (`/healthz`, `/readyz`),
  HSTS/CSP/secure-cookie hardening
- **Deploy**: multi-stage Dockerfile with Litestream, `docker-compose.prod.yml`
  (web + worker + Caddy), automatic HTTPS via Caddy

## Development

```sh
mise run install   # uv sync + pre-commit install
mise run migrate   # migrate + createcachetable --database cache
mise run dev       # runserver
mise run worker    # Django Tasks db_worker
mise run check     # ruff + pyright + pytest
```

## Deployment (VPS)

```sh
cp .env.example .env   # fill in secrets, domain, S3 credentials
docker compose -f docker-compose.prod.yml up -d --build
```

On boot the container restores `db.sqlite3` from the Litestream replica if the
data volume is empty, applies migrations, creates the cache table, then runs
`litestream replicate -exec gunicorn ...` so every write is continuously
replicated to S3-compatible storage.
