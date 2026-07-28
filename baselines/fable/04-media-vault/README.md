# media-vault

Media-heavy Django app: uploads land in S3 (MinIO locally), processing runs as
Redis-queued background tasks (`django.tasks` + RQ), and clients subscribe over
WebSockets (Channels) for status updates.

## Stack

- Django 6 with split settings (`config/settings/{base,local}.py`)
- PostgreSQL (Docker), psycopg 3
- ASGI via uvicorn + Channels (`channels-redis` channel layer)
- Background tasks: `django.tasks` with the `django-tasks-rq` RQ backend
- S3-compatible storage via `django-storages` (MinIO in local Compose)
- REST API: `django-modern-rest` (msgspec)
- Structured logging: `structlog` (pretty in dev, JSON otherwise), with a
  request-scoped `request_id` from `django-structlog`
- Tooling: `uv`, `ruff`, `pyright` + `django-stubs`

## Getting started

```sh
cp .env.example .env          # defaults match docker-compose.yml
uv sync
docker compose up -d          # db + redis + minio
uv run manage.py migrate
uv run manage.py createsuperuser --noinput   # admin/admin from .env
```

Run the app (HTTP + WebSockets share one process — `runserver` doesn't
upgrade WebSockets):

```sh
uv run uvicorn config.asgi:application --reload --host 0.0.0.0
```

Run a task worker in a second terminal:

```sh
uv run manage.py rqworker default
```

## Try it

Enqueue the sample background task:

```sh
uv run manage.py shell -c \
  "from jobs.tasks import process_media; print(process_media.enqueue('demo.png').id)"
```

Call the API:

```sh
curl -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename": "a.png", "size": 42}'
```

WebSocket echo endpoint: `ws://127.0.0.1:8000/ws/echo/` — any JSON you send
comes straight back.

Health checks: `GET /healthz` (liveness) and `GET /readyz` (checks
PostgreSQL + Redis).

MinIO console: http://127.0.0.1:9003 (minioadmin / minioadmin). Create the
`media` bucket once before uploading files through Django storage.

## Quality gates

```sh
uv run ruff check .
uv run pyright
uv run manage.py test
```
