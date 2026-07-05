# 02-shop

- Settings layout: split (`config/settings/{base,local,production,test}.py`).
- Database: PostgreSQL, host Postgres (not Docker). Dev DB name `shop_db`.
- Request handling: WSGI.
- Custom user model: `users.User` (email as `USERNAME_FIELD`, no `username`, extends `AbstractUser`).
- Auth: `django-allauth` (email login, mandatory verification in production) + `django-axes` (brute-force lockout). No 2FA.
- Cache: locmem (`LocMemCache`).
- Background tasks: none.
- Storage: WhiteNoise for static files (compressed, manifest-hashed in production). No media storage backend wired yet (`MEDIA_ROOT` is a local dir; add S3 before relying on user uploads on a managed platform).
- Email: SMTP in production (`EMAIL_URL`), console backend in local (`EMAIL_URL=consolemail://`). No HTML email base template.
- Billing: Stripe raw SDK (`stripe`) — customer id + `is_subscribed` on `users.User`, checkout/portal/webhook views in `billing/`.
- Frontend: Tailwind CSS (`django-tailwind-cli`, standalone binary, no Node) + DaisyUI, custom 404/403/500 templates, agent-drawn SVG favicon.
- SEO: meta/OG tags in `templates/base.html` + `django.contrib.sitemaps` (`/sitemap.xml`).
- `robots.txt`: yes, `config/views.py::robots_txt`.
- Health checks: `/healthz` (liveness), `/readyz` (DB reachable).
- Security: Django's HSTS / secure-cookie / SSL-redirect settings in `config/settings/production.py`. No `django-csp`.
- Database backups: `django-dbbackup`, local filesystem target (no S3 in scope for this project — swap `DBBACKUP_STORAGE` for an S3 backend if that changes).
- Lint: Ruff. Types: pyright + django-stubs. Tests: pytest + pytest-django. No pre-commit hooks. No i18n. No CI.
- Task runner: mise (`mise.toml`).
- Deploy: VPS via Docker (multi-stage `Dockerfile`, `python:3.12-slim-bookworm` runtime) + Caddy (`deploy/docker-compose.prod.yml`, `deploy/Caddyfile`).

## Layout

```
02-shop/
├── assets/                  # STATICFILES_DIRS — favicon.svg + compiled css/tailwind.css (gitignored)
├── billing/                 # Stripe checkout/portal/webhook views
├── config/
│   ├── settings/{base,local,production,test}.py
│   ├── sitemaps.py
│   ├── urls.py
│   ├── views.py             # robots.txt, healthz, readyz
│   ├── wsgi.py / asgi.py
├── deploy/
│   ├── docker-compose.prod.yml
│   └── Caddyfile
├── pages/                   # IndexView + pages/templates/pages/index.html
├── tailwind-src/css/        # source.css + vendored daisyui.mjs bundles
├── templates/                # base.html, 404/403/500.html
├── users/                   # custom User model (email login) + admin
├── Dockerfile
├── manage.py
├── mise.toml
├── pyproject.toml
├── .env.example
└── .env (gitignored)
```

## Key commands

```sh
cp .env.example .env          # then set a real DJANGO_SECRET_KEY
mise trust && mise install
mise run install
mise run migrate
mise run superuser
mise run tailwind              # tailwind watch + runserver
mise run dev                    # plain runserver
mise run test
mise run lint
mise run typecheck
mise run deploy                  # deploy-migrate then docker compose up -d, see deploy/
```

Fallback without mise: `uv run manage.py <command>` for every task above.
