# media-vault

Media-heavy app: uploads land in S3 (MinIO locally), processing runs as
Redis-queued background tasks (Django Tasks + RQ), and clients subscribe over
WebSockets for status updates (Channels).

## Stack

- Django 6, served over ASGI (`channels`) — HTTP and WebSockets share one process.
- PostgreSQL (Docker), Redis (Docker), MinIO/S3 (Docker) — Django, the RQ
  worker and uvicorn itself all run on the host.
- Background jobs: `django-tasks` with the `django-tasks-rq` backend.
- Real-time: `channels-redis` channel layer, `EchoConsumer` at `/ws/echo/`.
- REST API: `django-modern-rest` (`MediaController` at `POST /api/media/`).
- Structured logging: `structlog`, pretty console in dev / JSON in prod,
  request-scoped `request_id` via `django-structlog`.

## Setup

```bash
cp .env.example .env
uv sync
docker compose up -d
uv run manage.py migrate
uv run manage.py createsuperuser
```

Run the app (HTTP + WS in one process — `manage.py runserver` does not
upgrade WebSockets):

```bash
uv run uvicorn config.asgi:application --reload --host 0.0.0.0
```

In a separate terminal, run the RQ worker:

```bash
uv run manage.py rqworker default
```

## Verifying the setup

Enqueue the sample task from a shell:

```bash
uv run manage.py shell -c "
from jobs.tasks import process_media
result = process_media.enqueue('clip.mp4', 1024)
print(result.id)
"
```

The `rqworker` terminal should log `processing_media` and the job should show
`SUCCESSFUL` in the RQ dashboard (`/django-rq/`, once logged in as a staff user).

Check the WebSocket echo with `websocat` (or any WS client):

```bash
websocat ws://127.0.0.1:8000/ws/echo/
{"hello": "world"}
```

You should get `{"hello": "world"}` back.

Health check: `curl http://127.0.0.1:8000/healthz/`.

Media API:

```bash
curl -X POST http://127.0.0.1:8000/api/media/ \
  -H 'Content-Type: application/json' \
  -d '{"filename": "clip.mp4", "size": 1024}'
```

## Storage bucket

MinIO does not create buckets automatically. Create `media-vault` once, either
via the console at http://127.0.0.1:9001 (login `minioadmin` / `minioadmin`)
or with the `mc` CLI:

```bash
mc alias set local http://127.0.0.1:9000 minioadmin minioadmin
mc mb local/media-vault
```

## Tooling

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
uv run manage.py test
```
