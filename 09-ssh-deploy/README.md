## Prompt

```
/seedkit

Project name: 09-ssh-deploy
Purpose: production app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

Settings layout: split.
Database: PostgreSQL.
Postgres location: Postgres-in-Docker (`db` + `redis` services in `docker-compose.yml`, port `127.0.0.1:5432` published).
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): no.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: mise.
Add-ons:
  - redis
  - tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - analytics: Umami (self-hosted, env-driven website ID and host)
  - email: none (this project does not send transactional mail and the test verifies the skip path).
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: N/A (auth = none).
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.
  - Devcontainer: no.

Production setup:
  - apply Django security settings
  - CSP via `django-csp`: yes
  - error reporting: Bugsink (self-hosted, sentry-sdk DSN)
  - GDPR: PII scrubbing in error reports, retention defaults, user data export/delete
  - CI: GitHub Actions test workflow
  - deploy: GitHub Actions deploy via SSH (rsync + remote `docker compose pull && up -d`)
  - database backups via `django-dbbackup`: yes (self-managed host — no native backup service)
  - production Dockerfile: multi-stage — uv builder → `python:3.12-slim-bookworm` runtime

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `.github/workflows/test.yml`, `.github/workflows/deploy.yml`. Do not actually deploy — verify all artifacts are present, `docker build .` succeeds, and the deploy workflow references `secrets.SSH_HOST`, `secrets.SSH_USER`, `secrets.SSH_KEY`.
```

---

# 09-ssh-deploy

Production app deployed to a remote host over SSH from GitHub Actions, using self-hosted services.

## Stack

- Django 6, split settings (`config/settings/{base,local,production,test}.py`)
- PostgreSQL 17, Postgres-in-Docker for local dev (`docker-compose.yml`)
- Redis — cache + Django Tasks RQ broker
- Django Tasks with the Redis Queue backend (`django-tasks-rq` + `django-rq`); tasks live in `jobs/tasks.py`
- Structured logging via `structlog` + `django-structlog` — pretty console in dev, JSON in prod, per-request `request_id`
- Analytics: Umami (self-hosted, env-driven website id and host)
- Health checks: `/healthz` (liveness), `/readyz` (DB reachable)
- Lint: Ruff. Tests: pytest + pytest-django. No type checking, no pre-commit hooks, no i18n, no custom user model, no auth add-on.
- Task runner: mise (`mise.toml`)
- Security: Django's HSTS / secure-cookie / SSL-redirect settings + `django-csp` in `config/settings/production.py`
- Error reporting: Bugsink (self-hosted, Sentry-protocol) via `sentry-sdk`, with PII scrubbing (GDPR)
- User data export/delete management commands (`jobs/management/commands/`) for GDPR requests
- Database backups: `django-dbbackup` to an S3-compatible bucket (self-managed host, no native backup service)
- CI: GitHub Actions test workflow
- Deploy: GitHub Actions over SSH (rsync-free — builds + pushes a GHCR image, then `docker compose pull && migrate && up -d` on the host)
- Production Dockerfile: multi-stage — uv builder → `python:3.12-slim-bookworm` runtime

## Local dev ports

This dev machine already runs native Postgres (5432) and Redis (6379) outside Docker, so the local `docker-compose.yml` remaps to avoid bind conflicts:

- Postgres: `127.0.0.1:5435` → container `5432`
- Redis: `127.0.0.1:6381` → container `6379`

Adjust `DATABASE_URL` / `REDIS_URL` in `.env` (and the port mappings in `docker-compose.yml`) if your machine is free of conflicts and you'd rather use the standard `5432` / `6379`.

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
```

Fallback without mise: `uv run manage.py <command>` for every task above.

## Deploy

Secrets set in repo settings: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `GHCR_TOKEN` (a PAT with `read:packages`, used by the **server** to pull private images).

First deploy — create `deploy/.env.prod` on the host from `deploy/.env.prod.example`, then:

```sh
ssh user@host
cd /srv/09-ssh-deploy
export GITHUB_REPOSITORY=owner/repo
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
```

After that, `.github/workflows/deploy.yml` handles every push to `main`: it builds + pushes the image to GHCR, then SSHes in to pull, migrate, and restart. Database backups run via `django-dbbackup` — schedule `dbbackup` / `mediabackup` with a cron line on the host (see `references/dbbackup.md` in the seedkit skill for the exact crontab).

Built with [Seedkit](https://github.com/RobustaRush/seedkit).
