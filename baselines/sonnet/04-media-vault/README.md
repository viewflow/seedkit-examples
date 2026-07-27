# media-vault

Media-heavy Django app: uploads land in S3-compatible storage, processing runs as
Redis-queued background tasks, and clients subscribe over WebSockets for status
updates.

## Stack

- Django 6 (ASGI, split settings: `config/settings/{base,local,production}.py`)
- PostgreSQL (Postgres-in-Docker, `db` service)
- Channels + `channels-redis` for WebSockets (`/ws/echo/`)
- Django Tasks with the RQ backend (`django-tasks-rq`) for background jobs
- S3-compatible storage via `django-storages` (MinIO locally)
- `django-modern-rest` (msgspec + OpenAPI) for the JSON API (`api` app)
- `structlog` for structured logging (pretty console in dev, JSON in prod)
- Ruff for linting, `pyright` + `django-stubs` for type checking

## Setup

```sh
docker compose up -d                 # db + redis + minio
uv sync
cp .env.example .env                 # already gitignored

uv run manage.py migrate
uv run manage.py createsuperuser

# HTTP + WebSockets share one ASGI process — `runserver` doesn't upgrade WS.
uv run uvicorn config.asgi:application --reload --host 0.0.0.0

# in a separate terminal
uv run manage.py rqworker default
```

Visit `http://127.0.0.1:8000/admin/`, `GET /healthz`, `GET /readyz`.

## API

`POST /api/media/` — registers an upload.

```sh
curl -X POST http://127.0.0.1:8000/api/media/ \
  -H 'content-type: application/json' \
  -d '{"filename": "photo.png", "size": 1024}'
```

## Background tasks

`jobs/tasks.py` defines a sample `process_media` task, enqueued through
`django.tasks` / `django_tasks_rq`:

```python
from jobs.tasks import process_media

process_media.enqueue("some-uid", "photo.png")
```

Run a worker with `uv run manage.py rqworker default`.

## WebSockets

`EchoConsumer` at `/ws/echo/` echoes back any JSON message it receives. Test with:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:8000/ws/echo/", origin="http://localhost") as ws:
        await ws.send(json.dumps({"text": "ping"}))
        print(await ws.recv())

asyncio.run(main())
```

## Lint & type check

```sh
uv run ruff check .
uv run pyright
```

## Tests

```sh
uv run manage.py test
```
