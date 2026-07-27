# 02-shop — agent context

Small e-commerce site with admin and SMTP transactional email.

## Stack decisions

- Settings: split (`config/settings/base.py` / `local.py` / `production.py` / `test.py`)
- Database: PostgreSQL, host-installed (`DATABASE_URL`, dev DB `shop_db`)
- Request handling: WSGI
- Custom user model: `users.User`, email-only (`AUTH_USER_MODEL = "users.User"`, no `username` field)
- i18n: not applied
- Lint: Ruff (`uv run ruff check .` / `uv run ruff format .`)
- Test runner: pytest + pytest-django (`config.settings.test`)
- Type checking: pyright + django-stubs
- Task runner: mise (`mise.toml`)
- Auth: django-allauth — email login, mandatory email verification in production, no social providers
- Auth hardening: django-axes (no 2FA)
- Static/media: WhiteNoise (`CompressedManifestStaticFilesStorage` in production), media served locally in dev
- Email: `EMAIL_URL` — console backend in dev, SMTP in production
- Frontend: django-tailwind-cli + DaisyUI (`tailwind-src/css/source.css`, pinned Tailwind 4.3.2, DaisyUI v5.6.13 vendored bundles)
- Custom error templates: 404 / 403 / 500 (standalone, don't extend `base.html`)
- Favicon: agent-drawn SVG at `assets/favicon.svg`
- `pages` app: `IndexView` at `/`
- SEO: meta/OG tags in `templates/base.html`, `django.contrib.sitemaps` at `/sitemap.xml`
- `robots.txt`: `config/views.py::robots_txt`, toggle via `ROBOTS_DISALLOW_ALL`
- Browser auto-reload: django-browser-reload (dev only, gated by `INSTALLED_APPS` membership in `config/urls.py`, not raw `DEBUG` — the Docker build shims `DJANGO_DEBUG=True` against production settings for `tailwind build`/`collectstatic`, which must not pull in the dev-only app)
- Billing: raw `stripe` SDK — customer ID + subscription flag on `users.User`, Stripe-hosted Checkout + Customer Portal, webhook at `/billing/webhook/`
- Health checks: `/healthz` (liveness), `/readyz` (DB reachability) — `config/views.py`
- Security: `config/settings/production.py` — SSL redirect, HSTS, secure cookies, `DJANGO_BEHIND_PROXY` gate for `X-Forwarded-Proto` trust. CSP (`django-csp`) not applied.
- Deploy target: VPS — Docker Compose + Caddy (`deploy/docker-compose.prod.yml`, `deploy/Caddyfile`, `deploy/.env.prod.example`)
- Production image: multi-stage `Dockerfile` — `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` builder → `python:3.12-slim-bookworm` runtime (pin chosen to match this project's runtime target rather than the skill's default 3.13/trixie pin)
- `django-extensions`: not applied
- GDPR helpers, CI, error reporting, dbbackup: not applied

## Layout

```
02-shop/
├── config/
│   ├── settings/{base,local,production,test}.py
│   ├── urls.py, views.py (robots/health), sitemaps.py
│   ├── wsgi.py (production settings), asgi.py (production settings)
├── users/            # custom user model, admin
├── pages/            # IndexView at /
├── billing/          # stripe checkout/portal/webhook views
├── templates/        # base.html, index.html, 404/403/500.html
├── assets/           # STATICFILES_DIRS — favicon.svg, css/tailwind.css (built)
├── tailwind-src/css/ # source.css + vendored daisyui.mjs / daisyui-theme.mjs
├── deploy/           # docker-compose.prod.yml, Caddyfile, .env.prod.example
├── Dockerfile         # multi-stage production image
└── mise.toml
```

## Key commands

See README.md's Commands table. Short version:

```sh
mise run install    # uv sync
mise run migrate    # uv run manage.py migrate
mise run dev        # uv run manage.py runserver
mise run test       # uv run pytest
mise run lint       # uv run ruff check .
mise run typecheck  # uv run pyright
mise run deploy     # deploy-migrate then docker compose ... up -d (VPS)
```
