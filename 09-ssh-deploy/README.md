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
- PostgreSQL (Postgres-in-Docker for local dev — `db` + `redis` in `docker-compose.yml`)
- Redis — cache (`/0`) + `django-tasks-rq` queue (`/3`)
- Background tasks — Django Tasks with the Redis Queue backend (`django-tasks-rq`), app: `jobs`
- Structured logging — `structlog` + `django-structlog` (pretty console in dev, JSON in prod, request-scoped `request_id`)
- Analytics — Umami (self-hosted, env-driven website ID + host)
- Lint — Ruff
- Tests — pytest + pytest-django
- Task runner — mise
- Health checks — `/healthz` (liveness), `/readyz` (DB readiness)
- Security — Django deploy security settings + CSP (`django-csp`)
- Error reporting — Bugsink (self-hosted, Sentry protocol), PII scrubbed
- GDPR — user data export/delete management commands (`jobs/management/commands/`)
- Database backups — `django-dbbackup` to S3-compatible storage
- CI — GitHub Actions (`.github/workflows/test.yml`)
- Deploy — GitHub Actions via SSH: rsync-free, builds+pushes a GHCR image, then `ssh` runs `docker compose pull && migrate && up -d` (`.github/workflows/deploy.yml`)
- Production image — multi-stage: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` builder → `python:3.12-slim-bookworm` runtime

## Setup

```sh
cp .env.example .env   # then set a real DJANGO_SECRET_KEY
docker compose up -d   # db + redis
mise run install
mise run migrate
mise run superuser
mise run dev
```

Open <http://127.0.0.1:8000/admin/> and sign in.

In a second terminal, run the background worker:

```sh
mise run worker
```

Fallback without mise: `uv run manage.py <command>`.

## Commands

| Task | mise | Fallback |
| --- | --- | --- |
| install deps | `mise run install` | `uv sync` |
| run dev server | `mise run dev` | `uv run manage.py runserver` |
| migrate | `mise run migrate` | `uv run manage.py migrate` |
| makemigrations | `mise run makemigrations` | `uv run manage.py makemigrations` |
| shell | `mise run shell` | `uv run manage.py shell` |
| superuser | `mise run superuser` | `uv run manage.py createsuperuser` |
| test | `mise run test` | `uv run pytest` |
| lint | `mise run lint` | `uv run ruff check .` |
| format | `mise run fmt` | `uv run ruff format .` |
| task worker | `mise run worker` | `uv run manage.py rqworker default` |
| collectstatic | `mise run collectstatic` | `uv run manage.py collectstatic --noinput` |

First-time mise setup: `mise trust && mise install`.

## Local ports

The local `docker-compose.yml` publishes Postgres on `127.0.0.1:5433` and Redis on `127.0.0.1:6380`
(shifted from the defaults 5432/6379 to avoid clashing with any host-native Postgres/Redis already
running on this machine). `.env` matches these ports.

## Deploy

Deploy target: GitHub Actions via SSH. Every push to `main` runs the test workflow, builds and pushes
a Docker image to GHCR, then SSHes into the host and runs `docker compose pull && migrate && up -d`.

Repo secrets required: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `GHCR_TOKEN` (a PAT with `read:packages`,
used by the server to pull the private image).

First-time server setup:

```sh
ssh user@vps
mkdir -p /srv/09-ssh-deploy/deploy
cd /srv/09-ssh-deploy
# copy deploy/docker-compose.prod.yml, deploy/Caddyfile into place
cp deploy/.env.prod.example deploy/.env.prod   # fill in real secrets
export GITHUB_REPOSITORY=owner/repo IMAGE_TAG=latest
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml run --rm web python manage.py migrate
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
```

After that, every push to `main` deploys automatically. Rollback:

```sh
ssh user@vps
cd /srv/09-ssh-deploy
export GITHUB_REPOSITORY=owner/repo IMAGE_TAG=<known-good commit sha>
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull web
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d web
```

Built with [Seedkit](https://github.com/viewflow/seedkit).
