## Prompt

```
/seedkit

Project name: 07-vps-sqlite-saas
Purpose: production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

Settings layout: split.
Database: SQLite.
Lint with Ruff: yes.
Test runner: pytest + pytest-django.
Type check (pyright + django-stubs): yes.
Pre-commit hooks: yes.
Internationalisation (i18n): no.
Custom user model: yes (custom `users.User` extending `AbstractUser`).
Auth add-on: `django-allauth` (email login + mandatory verification).
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: mise.
Add-ons:
  - cache backend: sqlite (separate `cache.sqlite3` + `CacheRouter` + `DatabaseCache`)
  - tasks: Django Tasks with the Database backend (`django-tasks-db`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - storage: WhiteNoise (static), media volume on the VPS host
  - email: SMTP in production, console backend in local. Use a placeholder Postmark URL (`EMAIL_URL=smtp+tls://<token>:<token>@smtp.postmarkapp.com:587`); also wire `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`, `DJANGO_ADMINS`.
  - HTML email base template: no.
  - CORS: no.
  - REST API: none.
  - Frontend: none.
  - Auth hardening: `django-axes` (yes), 2FA (yes).
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.
  - Devcontainer: no.

Production setup:
  - apply Django security settings (HSTS, secure cookies, X-Frame, SSL redirect)
  - CSP via `django-csp`: yes
  - error reporting: Sentry SaaS (sentry-sdk)
  - CI: GitHub Actions test workflow
  - deploy target: VPS (Docker + Caddy)
  - database backups: Litestream replication to S3-compatible storage; do not use `django-dbbackup`
  - production Dockerfile: multi-stage with the Litestream `.deb` installed in the prod stage; ship `litestream.yml` + `entrypoint.sh` that restores the DB on boot, runs migrations, then execs `litestream replicate -exec "gunicorn ..."`
Skip GDPR for this case.

Run the foundation + boot check locally. Generate `Dockerfile`, `docker-compose.prod.yml`, `Caddyfile`, `litestream.yml`, `entrypoint.sh`, `.github/workflows/test.yml`. Do not actually push to a remote VPS — just verify all artifacts are present and `docker build .` succeeds.
```

---

# 07-vps-sqlite-saas

Production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack (no separate DB / cache / queue server).

## Stack

- Django 6, split settings (`config/settings/{base,local,production,test}.py`)
- SQLite (default DB + separate `cache.sqlite3` cache DB, WAL pragmas in production)
- Custom user model (`users.User`, email login, no username field)
- Auth: `django-allauth` (email login, mandatory verification in production) + `django-axes` (lockout) + `allauth.mfa` (TOTP 2FA)
- Background tasks: Django Tasks with the database backend (`django-tasks-db`) — sample task in `jobs/tasks.py`
- Email: SMTP in production (Postmark placeholder), console backend in local
- Static: WhiteNoise; media: local volume (Caddy-served on the VPS)
- Structured logging: `structlog` + `django-structlog` (JSON in prod, pretty console in dev, request-scoped `request_id`)
- Ruff (lint + format), pytest + pytest-django, pyright + django-stubs, pre-commit
- Security hardening (HSTS, secure cookies, SSL redirect) + CSP (`django-csp`)
- Error reporting: Sentry (`sentry-sdk`)
- CI: GitHub Actions (`.github/workflows/test.yml`)
- Deploy: VPS via Docker + Caddy, SQLite backups via Litestream → S3-compatible storage
- Task runner: `mise`

## Commands

```sh
mise trust && mise install     # first-time setup
mise run install                # uv sync
mise run dev                    # runserver
mise run migrate                # migrate
mise run makemigrations
mise run shell
mise run superuser              # createsuperuser
mise run test                   # pytest
mise run lint                   # ruff check
mise run fmt                    # ruff format
mise run typecheck              # pyright
mise run collectstatic
mise run worker                 # python manage.py db_worker
```

Fallback without mise: `uv run manage.py <command>`.

`cp .env.example .env` before the first run, then set a real `DJANGO_SECRET_KEY`.

## Deploy

```sh
ssh user@vps
cd /srv/07-vps-sqlite-saas
git pull
# --env-file is required on every compose call — compose auto-loads only ./.env, not deploy/.env.prod
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
docker image prune -f   # old :latest layers otherwise accumulate until the disk fills
```

No separate migrate step — `entrypoint.sh` restores the SQLite DB from the Litestream S3 replica (if present), runs `migrate --noinput` and `createcachetable`, then execs `litestream replicate` wrapping `gunicorn` on every container boot.

`mise run deploy` wraps the `up -d` step above. `collectstatic` runs at image build time (see `Dockerfile`), not on the VPS.

## SQLite + Litestream

- `DATABASE_URL=sqlite:////data/site.sqlite3` and `CACHE_DB_PATH=/data/cache.sqlite3` — both live on the `data` named volume.
- Litestream continuously replicates the WAL to S3-compatible storage (`S3_ENDPOINT` / `S3_BUCKET` / `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` in `deploy/.env.prod`).
- Single host only — no horizontal scaling. Deploys briefly stop writes during container swap.

Built with [Seedkit](https://github.com/viewflow/seedkit).
