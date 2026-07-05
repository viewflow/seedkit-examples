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

Production-ready SaaS skeleton deployed to a single VPS via docker-compose + Caddy, using the SQLite mini-prod stack — no separate DB / cache / queue server.

## Stack

| Layer | Choice |
|---|---|
| Framework | Django 6, split settings (`config/settings/{base,local,production,test}.py`) |
| Database | SQLite (WAL + IMMEDIATE pragmas in prod), `/data/site.sqlite3` on a persistent volume |
| Cache | Separate SQLite DB (`cache.sqlite3`) via `config.routers.CacheRouter` + `DatabaseCache` |
| Custom user model | `users.User` (email as `USERNAME_FIELD`, no `username`) |
| Auth | `django-allauth` (email login, mandatory verification in production) |
| Auth hardening | `django-axes` (lockout) + `allauth.mfa` (TOTP + recovery codes) |
| Background tasks | Django Tasks + `django-tasks-db` (database backend, no broker) — `jobs` app |
| Static files | WhiteNoise (compressed, manifest-hashed in production) |
| Media | Docker named volume, served by Caddy |
| Email | Console backend in dev, SMTP (Postmark placeholder) in production |
| Logging | `structlog` — pretty console in dev, JSON lines in prod, request-scoped `request_id` |
| Health checks | `/healthz` (liveness), `/readyz` (DB reachable) |
| Security | Django's HSTS / secure-cookie / SSL-redirect settings + `django-csp` |
| Error tracking | Sentry SaaS (`SENTRY_DSN` env var) |
| Lint/format | Ruff. **Types**: pyright + django-stubs. **Tests**: pytest + pytest-django. **Pre-commit**: yes |
| Task runner | mise (`mise.toml`) |
| CI | GitHub Actions (`ruff`, `pyright`, `manage.py check --deploy`, `pytest`) |
| Backups | Litestream — streams every WAL frame (site + cache DBs) to S3-compatible storage |
| Deploy | VPS via Docker + Caddy — multi-stage `Dockerfile` (`uv` builder → `python:3.13-slim-trixie` runtime) with Litestream baked in |

## Local development

Install [mise](https://mise.jdx.dev) (or run the underlying `uv run manage.py …` commands directly — see the fallback below).

```sh
cp .env.example .env   # then set a real DJANGO_SECRET_KEY

mise trust && mise install
mise run install
mise run migrate
uv run manage.py createcachetable --database cache
mise run superuser
mise run dev
```

Open <http://127.0.0.1:8000/admin/> and sign in with the new superuser.

| Task | Command |
| --- | --- |
| `mise run install` | `uv sync` |
| `mise run dev` | `uv run manage.py runserver` |
| `mise run migrate` | `uv run manage.py migrate` |
| `mise run makemigrations` | `uv run manage.py makemigrations` |
| `mise run shell` | `uv run manage.py shell` |
| `mise run superuser` | `uv run manage.py createsuperuser` |
| `mise run test` | `uv run pytest` |
| `mise run lint` | `uv run ruff check .` |
| `mise run fmt` | `uv run ruff format .` |
| `mise run typecheck` | `uv run pyright` |
| `mise run collectstatic` | `uv run manage.py collectstatic --noinput` |
| `mise run worker` | `uv run manage.py db_worker` |
| `mise run deploy` | see [Deploy](#deploy) |

No mise? Every task's command above runs directly with `uv run …`.

## Background tasks

Add tasks to `jobs/tasks.py`:

```python
from django_tasks import task

@task()
def my_task(arg: str) -> None:
    ...
```

Enqueue from anywhere:

```python
from jobs.tasks import my_task
my_task.enqueue("hello")
```

Run the worker locally alongside `runserver`:

```sh
mise run worker    # uv run manage.py db_worker
```

## Deploy

VPS with Docker + Caddy. The image bakes in Litestream — `entrypoint.sh` restores `site.sqlite3` / `cache.sqlite3` from the S3 replica on boot (a no-op on the very first deploy), runs migrations and `createcachetable`, then execs gunicorn under `litestream replicate` so every WAL frame streams out continuously. There is no separate `db` service — SQLite lives on the `data` named volume shared between `web` and `worker`.

```sh
ssh user@vps
cd /srv/07-vps-sqlite-saas
git pull
# --env-file is required on every compose call — compose auto-loads only ./.env, not deploy/.env.prod
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml pull
docker compose --env-file deploy/.env.prod -f deploy/docker-compose.prod.yml up -d
```

No separate one-shot `migrate` step before `up -d` — unlike the Postgres VPS pattern, `entrypoint.sh` runs `migrate --noinput` on every container boot after the Litestream restore.

Copy `.env.example` to `deploy/.env.prod` on the VPS and fill in real values — `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_BEHIND_PROXY=True`, a real `EMAIL_URL` (Postmark SMTP), `SENTRY_DSN`, and the Litestream `S3_*` vars. Also set `DATABASE_URL=sqlite:////data/site.sqlite3` and `CACHE_DB_PATH=/data/cache.sqlite3` so the app writes to the persistent volume instead of the image's build-time paths. Replace `example.com` in `deploy/Caddyfile` with the real domain before the first deploy.

`django-dbbackup` is intentionally not used — Litestream replicates every SQLite WAL frame to S3-compatible storage (R2, B2, Hetzner Object Storage, AWS S3) instead, which is finer-grained than periodic snapshots for a single-writer SQLite deploy.

## Environment variables

See `.env.example` for the full list.

---

Built with [Seedkit](https://github.com/RobustaRush/seedkit).
