# 07-vps-sqlite-saas

Production-ready Django SaaS skeleton meant to run on a single VPS via
docker-compose + Caddy, using a SQLite "mini-prod" stack (no separate DB,
cache, or queue server).

## Stack

- Django 5.1, split settings (`config/settings/{base,local,production,test}.py`)
- SQLite for the primary database, with a second `cache.sqlite3` database
  (routed via `config/routers.py`) backing `django.core.cache.backends.db.DatabaseCache`
- `django-tasks` + `django-tasks-db` (`db_worker` management command) for
  background jobs, sample task in `jobs/tasks.py`
- Custom user model (`users.User`), email login via `django-allauth`
  (mandatory email verification), MFA via `allauth.mfa`, brute-force
  protection via `django-axes`
- `structlog` + `django-structlog` for JSON logs in production / pretty
  console logs locally, request-scoped `request_id`
- WhiteNoise for static files, a host-mounted volume for media
- `django-csp`, HSTS/SSL-redirect/secure-cookie settings, Sentry error
  reporting in production
- Litestream replicates `db.sqlite3` continuously to S3-compatible storage
  and restores it on container boot
- `/healthz/` liveness endpoint checking both SQLite connections and the
  cache backend

## Local development

```sh
mise run setup      # uv sync + pre-commit install
mise run migrate    # migrate + create the cache table
mise run dev         # runserver
```

Other tasks: `mise run test`, `mise run lint`, `mise run format`,
`mise run typecheck`, `mise run check` (lint + typecheck + test),
`mise run worker` (runs the `db_worker` task consumer).

Copy `.env.example` to `.env` to override defaults; local dev works without
one since `config/settings/local.py` forces the console email backend and
disables `django-axes` lockouts.

## Production (VPS + Docker + Caddy)

```sh
cp .env.example .env   # fill in real secrets
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

- `app`: gunicorn behind `entrypoint.sh`, which restores the SQLite database
  from the Litestream replica (if the volume is empty), runs migrations,
  ensures the cache table exists, then execs
  `litestream replicate -exec "gunicorn ..."` so writes are continuously
  streamed to S3-compatible storage.
- `worker`: same image, runs `manage.py db_worker` to process background
  tasks against the same SQLite database.
- `caddy`: terminates TLS (automatic HTTPS via `$DOMAIN`), serves `/media/`
  directly from the shared volume, reverse-proxies everything else to `app`.

See `litestream.yml` for the replication config (reads `LITESTREAM_S3_*` env
vars) and `Dockerfile` for the multi-stage build (builder installs
dependencies with `uv`; the prod stage installs the Litestream `.deb`).
