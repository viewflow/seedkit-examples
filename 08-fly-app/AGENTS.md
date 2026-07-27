# 08-fly-app

Production app deployed to Fly.io with a slim multi-stage runtime image and S3-compatible object storage.

## Stack decisions

- Settings: split (`config/settings/{base,local,production,test,bolt}.py`)
- Database: PostgreSQL, Postgres-in-Docker locally (`db` service in `docker-compose.yml`, remapped to host port 5433 — see README's "Local port map")
- Request handling: WSGI
- Custom user model: no — auth add-on (`django-mail-auth`) supplies `mailauth.contrib.user.EmailUser` as `AUTH_USER_MODEL` instead
- Lint: Ruff
- Test runner: pytest + pytest-django (`config.settings.test`)
- Type checking: pyright + django-stubs
- Pre-commit hooks: no
- i18n: no
- Task runner: mise (`mise.toml`)
- Auth: `django-mail-auth` (passwordless magic-link), `mailauth.contrib.admin` wired ahead of `django.contrib.admin`
- Auth hardening: `django-axes` (lockout), no 2FA
- Redis: cache (`/0`) + Celery broker (`/1`) / result backend (`/2`)
- Background tasks: Celery
- Storage: S3-compatible (`django-storages[s3]`), MinIO locally (remapped to host port 9002/9003) / real S3 in prod
- Email: `django-anymail[postmark]`, console backend in dev, Anymail webhook wired at `/anymail/`
- REST API: `django-bolt` with the fast-path settings opt-in — `config/settings/bolt.py` + `config/urls_bolt.py` + `api/api.py`, separate process from `runserver`/gunicorn
- Analytics: GA4 (`ANALYTICS_ID`, `templates/_analytics.html`, `config/context_processors.py`)
- Frontend: none (minimal `templates/base.html` exists only so `_analytics.html` has somewhere to include)
- Health checks: `/healthz`, `/readyz` (`config/views.py`)
- Security: Django security settings + `django-csp` (GA4 hosts allowed in CSP directives) in `production.py`
- Error reporting: GlitchTip via `sentry-sdk`, PII scrubbing (`Authorization`/`Cookie` headers stripped)
- GDPR: `export_user_data` / `delete_user_data` management commands under `api/management/commands/`
- CI: GitHub Actions (`.github/workflows/test.yml`)
- Deploy: Fly.io managed (`fly.toml`, `[processes]` = web/worker/bolt), multi-stage `Dockerfile` (`python:3.12-slim-bookworm` runtime, pinned `linux/amd64` for django-bolt's compiled extension)

## Layout

```
config/
  settings/
    base.py         # shared settings, env-driven
    local.py         # dev overrides (none beyond base)
    production.py    # security, CSP, GlitchTip, S3 static flip, axes cache handler
    test.py           # pytest settings — locmem cache/email, in-memory storage
    bolt.py           # fast-path settings for the django-bolt process
  urls.py            # admin, mailauth, anymail webhook, healthz/readyz
  urls_bolt.py        # empty — runbolt discovers routes from BoltAPI() directly
  views.py           # liveness/readiness views
  context_processors.py  # GA4 analytics context
  celery.py           # Celery app
api/
  api.py             # BoltAPI() — GET /users/{user_id}
  management/commands/
    export_user_data.py
    delete_user_data.py
templates/
  base.html          # minimal — frontend=none
  _analytics.html    # GA4 snippet
  registration/      # mailauth login templates
docker-compose.yml   # db + redis + minio (remapped host ports — see README)
Dockerfile           # multi-stage: uv builder → python:3.12-slim-bookworm runtime
fly.toml
mise.toml
.github/workflows/test.yml
```

## Key commands

| Task | Command |
|---|---|
| Install | `mise run install` |
| Dev server | `mise run dev` |
| Migrate | `mise run migrate` |
| Test | `mise run test` |
| Lint | `mise run lint` |
| Type check | `mise run typecheck` |
| Worker | `mise run worker` |
| Bolt API | `DJANGO_SETTINGS_MODULE=config.settings.bolt uv run manage.py runbolt --dev --port 8001` |
| Deploy | `mise run deploy` (`fly deploy`) |

Fallback: `uv run manage.py <command>`.

## Gotchas

- `manage.py makemigrations --check --dry-run` is scoped to `api` in CI — an unscoped
  run always flags a phantom `id` field diff on the vendored `mailauth_user` app because
  its shipped migration predates this project's `DEFAULT_AUTO_FIELD = BigAutoField`.
- `api/api.py`'s `UserSchema.username` is populated from `EmailUser.email` — the chosen
  auth add-on has no username column.
