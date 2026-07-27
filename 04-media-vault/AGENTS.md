# 04-media-vault

Media-heavy app: uploads to S3, Redis-queued background processing, WebSocket
status updates.

## Stack decisions

- Settings layout: split (`config/settings/base.py` + `local.py` / `production.py` / `test.py`)
- Database: PostgreSQL, Postgres-in-Docker (`db` service, `docker-compose.yml`)
- Request handling: ASGI + Channels (`config/asgi.py` — `ProtocolTypeRouter` + `AllowedHostsOriginValidator` + `AuthMiddlewareStack`)
- Lint: Ruff
- Test runner: stock `manage.py test`
- Type checking: pyright + django-stubs
- Pre-commit hooks: none
- i18n: none
- Custom user model: none
- Auth: none
- Structured logging: `structlog` + `django-structlog`, JSON in prod / pretty console in dev, request-scoped `request_id`
- Task runner (shell task wrapper): none — use `uv run manage.py …` directly
- Redis: `django-redis` cache backend (`/0`)
- Storage: S3-compatible via `django-storages`, MinIO in local Compose
- Background tasks: Django Tasks on the RQ backend (`django-tasks-rq` + `django-rq`, broker `/3`)
- Real-time: `channels` + `channels-redis` (layer `/4`), `EchoConsumer` at `/ws/echo/`
- Email: console backend in dev
- CORS: `django-cors-headers`
- REST API: `django-modern-rest` (msgspec + OpenAPI extras), `MediaController` — `POST /api/media/`
- Frontend: none
- Devcontainer: yes (`.devcontainer/devcontainer.json`)
- Health checks: `/healthz` (liveness), `/readyz` (DB readiness)
- `robots.txt`: none
- `django-extensions`: none
- Production deploy: skipped for this run — no production Dockerfile / deploy compose

## Known upstream quirk

`django-modern-rest` 0.11.0's `dmr.throttling` module unconditionally imports
`jwt` even when the `[jwt]` extra isn't installed (`dmr/security/jwt/__init__.py`
re-raises `ImportError` after printing a warning). `pyjwt` is pinned as a plain
dependency (not the `[jwt]` extra, no crypto backend) purely to satisfy that
import — JWT auth itself is not wired up.

## Project layout

```
config/
  settings/
    base.py          # env-driven core settings, all add-on wiring
    local.py          # dev delta (empty — Redis is always up via Compose)
    production.py      # S3 static override
    test.py            # locmem cache/email, in-memory storage, immediate tasks
  asgi.py              # ProtocolTypeRouter (HTTP + WS), settings -> production
  wsgi.py              # unused (asgi+channels mode) — startproject default, not loaded
  routing.py            # websocket_urlpatterns -> EchoConsumer at /ws/echo/
  urls.py               # /, /admin/, /django-rq/, /healthz, /readyz, /api/*
  views.py              # liveness / readiness views
jobs/                   # background tasks + WebSocket consumer
  apps.py               # ready() imports tasks.py to register @task functions
  tasks.py              # process_media sample task
  consumers.py          # EchoConsumer (AsyncJsonWebsocketConsumer)
api/                    # django-modern-rest app (not in INSTALLED_APPS — no OpenAPI UI wired)
  schemas.py            # MediaCreate / Media msgspec structs
  controllers.py        # MediaController.post
  urls.py               # dmr Router, prefix "api/"
docker-compose.yml      # db (Postgres), redis, minio — local services only
```

## Key commands

```sh
uv sync
docker compose up -d --wait
uv run manage.py migrate
uv run manage.py createsuperuser
uv run uvicorn config.asgi:application --reload --host 0.0.0.0   # HTTP + WS
uv run manage.py rqworker default                                 # separate terminal
uv run manage.py test
uv run ruff check .
uv run ruff format .
uv run pyright
docker compose down -v
```
