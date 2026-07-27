# 07-vps-sqlite-saas

Production-ready Django SaaS skeleton for a single VPS: `docker-compose` + Caddy,
SQLite for both the primary database and the cache (no separate DB/cache/queue
server), and Litestream replicating both `.sqlite3` files to S3-compatible
storage for backups.

## Stack

- Django 5.1, split settings (`config/settings/{base,local,production,test}.py`)
- SQLite: `db.sqlite3` (default) + `cache.sqlite3` (cache, via `CacheRouter` +
  `DatabaseCache`)
- Custom user model (`users.User`, email login, no username)
- `django-allauth` — email login, mandatory email verification, TOTP 2FA
  (`allauth.mfa`)
- `django-axes` — login throttling / lockout
- `django-tasks` + `django-tasks-db` — background tasks via the database
  backend (see `jobs/tasks.py`)
- `structlog` / `django-structlog` — JSON logs in production, pretty console
  logs locally, request-scoped `request_id`
- WhiteNoise for static files, a media volume on the VPS host
- SMTP email in production (Postmark via `EMAIL_URL`), console backend locally
- `django-csp`, HSTS/secure cookies/SSL redirect in production
- Sentry error reporting
- Litestream replication + restore-on-boot
- Ruff, pytest + pytest-django, pyright + django-stubs, pre-commit

## Local development

```sh
mise run setup      # uv sync + pre-commit install
mise run migrate
uv run manage.py createcachetable --database cache
uv run manage.py createsuperuser
mise run dev         # http://127.0.0.1:8000
```

Health checks: `GET /healthz` (liveness) and `GET /readyz` (both sqlite
databases reachable).

## Checks

```sh
mise run lint        # ruff check
mise run format       # ruff format
mise run typecheck    # pyright
mise run test          # pytest
mise run check          # lint + typecheck + test
```

## Deploying to a VPS

1. Copy `.env.example` to `.env` and fill in `SECRET_KEY`, `ALLOWED_HOSTS`,
   `EMAIL_URL` (Postmark SMTP), `SENTRY_DSN`, and the `LITESTREAM_*` S3
   credentials.
2. `docker compose -f docker-compose.prod.yml up -d --build`

The `app` container's `entrypoint.sh`:

1. restores `db.sqlite3` from the Litestream S3 replica if no local copy exists,
2. runs `migrate` and `createcachetable`,
3. execs `litestream replicate -exec "gunicorn ..."` so writes are continuously
   streamed to S3 while gunicorn serves traffic.

Caddy terminates TLS (set `SITE_ADDRESS` in `.env` to your domain) and reverse
proxies to `app:8000`; it also serves the `media` volume directly.

Database files live in the `db-data` volume; media in `media-data`. Both are
independent of the container filesystem, so redeploys don't lose data — the
source of truth is still the S3 Litestream replica.
