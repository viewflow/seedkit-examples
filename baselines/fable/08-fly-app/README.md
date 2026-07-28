# 08-fly-app

Production Django app deployed to Fly.io with a slim multi-stage runtime image
and S3-compatible object storage (MinIO locally, S3 in production).

## Stack

- Django 6 with split settings (`config/settings/{base,local,production,test,bolt}.py`)
- PostgreSQL, Redis (cache + Celery broker), MinIO — all via `docker-compose.yml`
- Passwordless magic-link auth (`django-mail-auth`) guarded by `django-axes`
- Transactional email via Anymail/Postmark in production, console backend in dev
- REST API on `django-bolt` (Rust HTTP layer) with fast-path settings (`config.settings.bolt`)
- Celery worker + beat (session retention purge)
- GlitchTip error reporting (sentry-sdk, PII scrubbed), django-csp, GA4
- GDPR: data export (`/privacy/export/`) and account deletion (`/privacy/delete/`)

## Quick start

```sh
mise run setup      # uv sync + docker compose up -d (db, redis, minio)
mise run migrate
mise run dev        # http://127.0.0.1:8000
mise run worker     # celery worker
mise run bolt       # django-bolt API on http://127.0.0.1:8001
```

Health probes: `/healthz` (liveness), `/readyz` (DB + cache readiness).

## Checks

```sh
mise run test        # pytest
mise run lint        # ruff
mise run typecheck   # pyright
```

## Deploy

`fly.toml` defines three processes — `web` (gunicorn), `worker` (celery) and
`bolt` (`manage.py runbolt` under `config.settings.bolt`). Release command runs
migrations. Build with the multi-stage `Dockerfile` (runtime stage:
`python:3.12-slim-bookworm`, no uv, non-root user).

Required production secrets: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`,
`POSTMARK_SERVER_TOKEN`, `ANYMAIL_WEBHOOK_SECRET`, AWS S3 credentials,
`GLITCHTIP_DSN` (optional), `GA4_MEASUREMENT_ID` (optional).
