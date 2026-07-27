## Prompt

```
/seedkit

Project name: 04-media-vault
Purpose: media-heavy app where uploads land in S3, processing runs as Redis-queued background tasks, and clients subscribe over WebSockets for status updates.

Settings layout: split.
Database: PostgreSQL.
Request handling: asgi+channels.
Postgres location: Postgres-in-Docker (`db` service in `docker-compose.yml`, port `127.0.0.1:5432` published).
Lint with Ruff: yes.
Test runner: manage.py test (stock Django).
Type check (pyright + django-stubs): yes.
Pre-commit hooks: no.
Internationalisation (i18n): no.
Custom user model: no.
Auth add-on: none.
Structured logging: yes (`structlog`, JSON in prod / pretty in dev, request-scoped `request_id`).
Task runner: none.
Add-ons:
  - redis
  - storage: S3-compatible (use MinIO in local Compose; configure via env)
  - tasks: Django Tasks with the Redis Queue backend (`django-tasks-rq`). Also `uv run manage.py startapp jobs`, register `jobs` in `INSTALLED_APPS`, wire `jobs/apps.py` `ready()` to import `tasks`, and add a sample `@task` to `jobs/tasks.py`.
  - real-time channel layer: `channels-redis` (reuse the same Redis service). Add an `EchoConsumer` (`AsyncJsonWebsocketConsumer`) that echoes received JSON back to the sender, routed at `/ws/echo/` in `config/routing.py`. Wire `config/asgi.py` with `ProtocolTypeRouter` + `AllowedHostsOriginValidator` + `AuthMiddlewareStack`.
  - email: console backend in local (`EMAIL_URL=consolemail://`).
  - HTML email base template: no.
  - CORS: yes.
  - REST API: `django-modern-rest` with the `msgspec` + `openapi` extras (`uv add 'django-modern-rest[msgspec,openapi]'`). Create an `api` app (`uv run manage.py startapp api`) with a single `MediaController` exposing `POST /api/media/` that accepts `{ "filename": str, "size": int }` (msgspec.Struct) and returns `{ "uid": uuid, "filename": str }`. Wire the `Router` from `api/urls.py` into `config/urls.py` under the `api` namespace. Do NOT add `dmr` to `INSTALLED_APPS`.
  - Frontend: none.
  - Devcontainer: yes.
  - Health check endpoints: yes.
  - `robots.txt`: no.
  - `django-extensions`: no.

Production setup: skip.

Generate `docker-compose.yml` with services `db`, `redis`, `minio` (local services only — Django, the rqworker, and uvicorn run on the host). Run the foundation, `docker compose up -d`, `uv run uvicorn config.asgi:application --reload --host 0.0.0.0` (HTTP + WS share one process in dev — `manage.py runserver` doesn't upgrade WebSockets), `uv run manage.py rqworker default` in a separate terminal, migrate, createsuperuser, and confirm a sample task enqueues and a WebSocket round-trip works.
```

---

# 04-media-vault

Media-heavy app where uploads land in S3, processing runs as Redis-queued
background tasks, and clients subscribe over WebSockets for status updates.

## Stack

- Django 6, split settings (`config/settings/{base,local,production,test}.py`)
- PostgreSQL (Postgres-in-Docker, `db` service)
- Request handling: ASGI + Channels (WebSockets), served by `uvicorn` in dev
- Redis (cache, Channels layer, RQ broker — see the DB map below)
- S3-compatible storage via `django-storages` (MinIO in local Compose)
- Background tasks: Django Tasks on the Redis Queue backend (`django-tasks-rq`)
- Real-time: `channels` + `channels-redis`, `EchoConsumer` at `/ws/echo/`
- REST API: `django-modern-rest` (msgspec + OpenAPI extras), `MediaController` at `POST /api/media/`
- Structured logging: `structlog` + `django-structlog` (pretty console in dev, JSON in prod)
- CORS: `django-cors-headers`
- Email: console backend in dev
- Lint: Ruff. Type check: pyright + django-stubs. Tests: stock `manage.py test`
- Devcontainer included

Production deploy artifacts were skipped for this run.

## Redis DB map

| DB | Consumer |
|----|----------|
| `/0` | cache (`django-redis`) |
| `/3` | django-tasks-rq broker |
| `/4` | Channels layer |

## Local ports

`db` and `redis` are published on non-default host ports because this machine
already runs a host-level Postgres (`5432`) and Redis (`6379`, both via
Homebrew services) outside this project:

- Postgres: `127.0.0.1:5433` → container `5432`
- Redis: `127.0.0.1:6380` → container `6379`
- MinIO: `127.0.0.1:9000` (S3 API), `127.0.0.1:9001` (console)

`.env` / `.env.example` already point at these ports. If your machine doesn't
have anything else bound to 5432/6379, feel free to remap back to the
defaults.

## Setup

```sh
cp .env.example .env    # already done in this repo; regenerate DJANGO_SECRET_KEY for a new clone
uv sync
docker compose up -d --wait      # db + redis + minio
uv run manage.py migrate
uv run manage.py createsuperuser
```

## Run

HTTP and WebSockets share one process in dev — `manage.py runserver` does not
upgrade WebSocket connections, so run uvicorn directly:

```sh
uv run uvicorn config.asgi:application --reload --host 0.0.0.0
```

In a second terminal, the RQ worker:

```sh
uv run manage.py rqworker default
```

Visit `/admin/` to sign in, `/django-rq/` for the queue dashboard.

## Verify

```sh
# Enqueue + process a sample task
uv run manage.py shell -c "from jobs.tasks import process_media; process_media.enqueue('sample.png', 1024)"

# REST endpoint
curl -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename":"a.png","size":42}'

# WebSocket echo (wscat, websocat, or any client that sends an Origin header)
```

## Test / lint / typecheck

```sh
uv run manage.py test
uv run ruff check .
uv run ruff format .
uv run pyright
```

## Teardown

```sh
docker compose down -v
```

Built with [Seedkit](https://github.com/viewflow/seedkit).
