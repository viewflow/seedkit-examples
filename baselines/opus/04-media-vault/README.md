# 04-media-vault

Media-heavy Django app: uploads land in S3-compatible storage, processing runs
as Redis-queued background tasks, and clients subscribe over WebSockets for
status updates.

- **ASGI + Channels** — HTTP and WebSocket served from one uvicorn process
- **PostgreSQL** in Docker, **Redis** for the cache, channel layer and queue
- **MinIO** locally as the S3 endpoint (swap `AWS_S3_ENDPOINT_URL` for real AWS)
- **Django Tasks** on the RQ backend (`django-tasks-rq`)
- **django-modern-rest** with `msgspec` schemas and a generated OpenAPI 3.1 spec
- **structlog** — pretty console in dev, JSON in prod, request-scoped `request_id`

## Layout

```
config/
  settings/{base,local,production}.py   split settings
  asgi.py            ProtocolTypeRouter: HTTP + WebSocket
  routing.py         WebSocket URLs
  consumers.py       EchoConsumer
  urls.py            HTTP URLs
  health.py          /healthz (liveness), /readyz (Postgres + Redis)
  logging.py         structlog config + RequestIDMiddleware
api/
  schemas.py         msgspec Structs
  controllers.py     MediaController
  urls.py            dmr Router
jobs/
  tasks.py           @task process_media
```

## Getting started

```sh
cp .env.example .env
docker compose up -d          # db + redis + minio (+ one-shot bucket create)
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
```

Two terminals — `manage.py runserver` does **not** upgrade WebSocket
connections, so use uvicorn even in development:

```sh
uv run uvicorn config.asgi:application --reload --host 0.0.0.0
uv run manage.py rqworker default
```

### If the host already runs Postgres or Redis

The compose ports default to `5432`/`6379` but are overridable. Set
`POSTGRES_PORT` / `REDIS_PORT` in `.env` and keep `DATABASE_URL` / `REDIS_URL`
pointing at the same numbers, rather than stopping the host's services.

## Endpoints

| Path                | What it does                                       |
| ------------------- | -------------------------------------------------- |
| `POST /api/media/`  | `{filename, size}` → `{uid, filename}`, queues work |
| `GET /api/openapi.json` | Generated OpenAPI 3.1 schema                   |
| `ws://…/ws/echo/`   | Echoes received JSON back to the sender            |
| `GET /healthz`      | Liveness — touches nothing external                |
| `GET /readyz`       | Readiness — Postgres and Redis round-trip          |
| `/admin/`, `/django-rq/` | Django admin and the RQ dashboard             |

Quick check:

```sh
curl -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' -d '{"filename":"a.png","size":42}'
```

The worker log then shows `media.processing.started` / `finished`.

`AllowedHostsOriginValidator` guards the WebSocket, so clients must send an
`Origin` whose host is in `DJANGO_ALLOWED_HOSTS`.

## Development

```sh
uv run manage.py test    # stock Django test runner
uv run ruff check .
uv run pyright
./smoke.sh               # boots everything and runs the end-to-end checks
```

`dmr` is deliberately **not** in `INSTALLED_APPS` — the framework does not need
it. The trade-off is that its bundled Swagger/Redoc templates are unavailable,
so only the JSON schema is served.

A devcontainer is provided under `.devcontainer/`; it reaches the services by
DNS name (`db`, `redis`, `minio`) instead of the published host ports.
