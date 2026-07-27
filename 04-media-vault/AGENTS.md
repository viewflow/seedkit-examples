# 04-media-vault

Media-heavy app: uploads land in S3, processing runs as Redis-queued background tasks, clients subscribe over WebSockets for status updates.

## Stack decisions

- Settings layout: split (`config/settings/base.py` + `local.py` / `production.py` / `test.py`)
- Database: PostgreSQL, Postgres-in-Docker (`db` service, published on `127.0.0.1:5432`)
- Request handling: asgi+channels — `daphne` in `INSTALLED_APPS`, `uvicorn` serves dev, `gunicorn -k uvicorn_worker.UvicornWorker` would serve prod
- Ruff lint: yes
- Test runner: stock `manage.py test`
- Type checking: pyright + django-stubs
- Pre-commit hooks: no
- i18n: no
- Custom user model: no
- Auth add-on: none
- Structured logging: structlog, JSON in prod / pretty console in dev, request-scoped `request_id` via `django_structlog.middlewares.RequestMiddleware`
- Task runner (mise/just/make): none — use `uv run manage.py …` directly
- Redis: cache (`/0`), django-tasks-rq broker (`/3`), channels layer (`/4`)
- Storage: S3-compatible via `django-storages[s3]`, MinIO locally
- Background tasks: Django Tasks + `django-tasks-rq` (RQ backend) — `jobs` app, sample task in `jobs/tasks.py`
- Real-time: `channels` + `channels-redis`, `EchoConsumer` at `/ws/echo/`
- Email: console backend in local (`EMAIL_URL=consolemail://`)
- CORS: `django-cors-headers`
- REST API: `django-modern-rest[msgspec,openapi]` — `api` app, `MediaController` at `POST /api/media/`. `dmr` is NOT in `INSTALLED_APPS` (not needed for plain endpoints)
- Frontend: none
- Devcontainer: yes (`.devcontainer/devcontainer.json`)
- Health checks: yes (`/healthz`, `/readyz`)
- `robots.txt`: no
- `django-extensions`: no
- Production setup: skipped (no Dockerfile / deploy target)

## Layout

```
config/
  settings/
    base.py         # env-driven settings, all add-on config
    local.py         # dev delta (empty — base covers it)
    production.py     # prod delta (S3 static flip)
    test.py           # fast/deterministic test overrides
  asgi.py             # ProtocolTypeRouter + AllowedHostsOriginValidator + AuthMiddlewareStack
  routing.py          # websocket_urlpatterns
  consumers.py        # EchoConsumer
  urls.py
  views.py            # healthz / readyz
api/
  controllers.py      # MediaController
  schemas.py          # msgspec Structs
  urls.py             # dmr Router
jobs/
  apps.py             # ready() imports tasks
  tasks.py            # sample @task
docker-compose.yml    # db + redis + minio (local only)
```

## Key commands

```sh
docker compose up -d                                              # db + redis + minio
uv run manage.py migrate
uv run manage.py createsuperuser
uv run uvicorn config.asgi:application --reload --host 0.0.0.0    # HTTP + WS (runserver won't upgrade WS)
uv run manage.py rqworker default                                 # separate terminal
uv run manage.py test
uv run ruff check .
uv run ruff format .
uv run pyright
```
