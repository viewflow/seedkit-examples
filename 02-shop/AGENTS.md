# Shop

Small e-commerce site with admin and SMTP transactional email.

## Stack decisions

- Settings layout: split — `config/settings/base.py`, `local.py`, `production.py`, `test.py`
- Database: PostgreSQL, host Postgres in dev (`DATABASE_URL`), Postgres 17 in Docker prod
- Request handling: WSGI (gunicorn in production)
- Custom user model: `users.User`, email as `USERNAME_FIELD`, no `username` field
- Auth: `django-allauth` — email login, mandatory verification in production, no social providers
- Auth hardening: `django-axes` — 5-attempt lockout, 1h cooloff, no 2FA
- Lint: Ruff (`ruff check` / `ruff format`)
- Tests: pytest + pytest-django (`config.settings.test`)
- Type checking: pyright + django-stubs
- Pre-commit hooks: none
- i18n: none (`USE_I18N` not set)
- Task runner: mise (`mise.toml`)
- Static storage: WhiteNoise, `CompressedManifestStaticFilesStorage` in production, no media volume yet
- Email: SMTP — console backend in dev, real SMTP in production via `EMAIL_URL`
- Frontend: `django-tailwind-cli` + DaisyUI (vendored `tailwind-src/css/daisyui{,-theme}.mjs`, pinned v5.7.4), custom 404/403/500 templates, agent-drawn SVG favicon
- `pages` app: `IndexView` (`TemplateView`) wired at `/`
- SEO: meta/OG tags in `templates/base.html`, `sitemap.xml` via `django.contrib.sitemaps`
- `robots.txt`: `config/views.py` — disallow-all in dev, disallow `/admin/` + `/accounts/` in production
- Billing: `stripe` raw SDK — Customer/Checkout/Portal/webhook views in `billing/`, `stripe_customer_id` + `is_subscribed` on `users.User`
- Health checks: `/healthz` (liveness), `/readyz` (DB readiness) in `config/views.py`
- Browser auto-reload: `django-browser-reload`, dev-only (`INSTALLED_APPS` membership check in `config/urls.py`, not a bare `DEBUG` check — production settings never installs it even under the Tailwind-build `DEBUG=True` shim)
- Database backups: skipped — `django-dbbackup` requires S3-compatible storage, which wasn't part of this project's storage add-on scope
- Production: multi-stage `Dockerfile` (`ghcr.io/astral-sh/uv:python3.12-bookworm-slim` builder → `python:3.12-slim-bookworm` runtime), deploy target VPS (Docker Compose + Caddy)
- Security: `config/settings/production.py` — HTTPS redirect, secure cookies, HSTS, `CSRF_TRUSTED_ORIGINS` from env

## Layout

```
config/
  settings/
    base.py        # shared settings, env-driven
    local.py        # dev: browser-reload
    production.py    # prod: security, WhiteNoise, mandatory email verification
    test.py           # pytest: locmem email/cache, fast hasher
  urls.py
  views.py           # robots.txt, healthz, readyz
  sitemaps.py
  wsgi.py / asgi.py   # both point at config.settings.production
users/                # custom User model (email login)
pages/                 # IndexView at /
billing/                # stripe checkout / portal / webhook views
templates/
  base.html, index.html, 404.html, 403.html, 500.html
assets/                 # STATICFILES_DIRS[0] — favicon.svg, compiled css/tailwind.css
tailwind-src/css/       # source.css + vendored DaisyUI plugin bundles
deploy/
  docker-compose.prod.yml, .env.prod.example, Caddyfile
Dockerfile
mise.toml
```

## Key commands

```sh
mise run install
mise run dev
mise run migrate
mise run makemigrations
mise run shell
mise run superuser
mise run test
mise run lint
mise run fmt
mise run typecheck
mise run collectstatic
mise run tailwind
mise run deploy-migrate
mise run deploy
```

Fallback without mise: `uv run manage.py <command>`.
