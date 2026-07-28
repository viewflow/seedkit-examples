# 09-ssh-deploy

Production Django app deployed to a self-managed host over SSH from GitHub
Actions, running on self-hosted services (Postgres, Redis, Umami, Bugsink).

## Stack

- Django 6 with split settings (`config/settings/{base,dev,prod,test}.py`)
- PostgreSQL 17 + Redis 8 (Docker for local dev, compose stack in prod)
- Background tasks: Django Tasks with the RQ backend (`django-tasks-rq`)
- Structured logging: `structlog` — pretty console in dev, JSON in prod,
  request-scoped `request_id` via `django-structlog`
- Analytics: self-hosted Umami (env-driven, CSP-whitelisted)
- Error reporting: self-hosted Bugsink via `sentry-sdk`, with GDPR PII scrubbing
- Security: Django hardening + CSP (`django-csp`)
- Backups: `django-dbbackup` to a local volume, 14 most recent kept
- Tooling: `uv`, `mise`, `ruff`, `pytest`

## Development

```sh
mise run up        # start db + redis (docker compose)
uv sync
uv run manage.py migrate
mise run dev       # runserver
mise run worker    # rq worker for background tasks
mise run test      # pytest
mise run lint      # ruff
```

Health endpoints: `GET /healthz` (liveness) and `GET /readyz` (DB + Redis
readiness).

## GDPR

- Error reports are scrubbed of PII before leaving the host
  (`core/gdpr.py:scrub_sentry_event`, `send_default_pii=False`).
- Retention defaults: `DATA_RETENTION_DAYS` (365), 14 rotated DB backups,
  two-week sessions.
- Subject requests: `manage.py gdpr_export_user <username>` and
  `manage.py gdpr_delete_user <username>`.

## Deployment

`main` is tested by `.github/workflows/test.yml`, then
`.github/workflows/deploy.yml`:

1. builds the multi-stage image (`uv` builder → `python:3.12-slim-bookworm`)
   and pushes it to GHCR;
2. rsyncs `docker-compose.prod.yml` to the server (`secrets.SSH_HOST`,
   `secrets.SSH_USER`, `secrets.SSH_KEY`);
3. runs `docker compose pull && up -d` remotely, applies migrations, and
   verifies `/readyz`.

Server prerequisites: Docker with the compose plugin, `/opt/09-ssh-deploy/.env`
(see `.env.example` — must define `WEB_IMAGE` and secrets), and a reverse proxy
forwarding to `127.0.0.1:8000` with the `X-Forwarded-Proto` header set.

Backups: schedule `docker compose -f docker-compose.prod.yml exec -T web
python manage.py dbbackup --clean` from cron on the host.
