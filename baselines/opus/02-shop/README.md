# 02-shop

A small e-commerce site: a product catalogue, Django admin, Stripe Checkout, and
transactional e-mail over SMTP.

## Stack

| Concern | Choice |
| --- | --- |
| Framework | Django 5.2, split settings (`config/settings/{base,local,production}.py`) |
| Database | PostgreSQL (via `DATABASE_URL`) |
| Auth | Custom `users.User` (e-mail login) + django-allauth, mandatory verification |
| Hardening | django-axes lockout, security headers in production |
| Payments | Stripe (raw SDK) — Checkout Sessions plus a signed webhook |
| Frontend | Tailwind CSS v4 + DaisyUI via `django-tailwind-cli` (standalone binary, no Node) |
| Static files | WhiteNoise |
| Tooling | uv, mise, Ruff, pyright + django-stubs, pytest + pytest-django |
| Deployment | Docker (multi-stage, uv builder) behind Caddy |

## Getting started

```sh
mise install          # python + uv
uv sync               # create .venv from uv.lock
cp .env.example .env  # then edit
createdb shop_db
uv run manage.py migrate
uv run manage.py tailwind build
uv run manage.py createsuperuser
uv run manage.py runserver
```

The site is then at <http://127.0.0.1:8000/>, the admin at `/admin/`.

While developing, run `mise run watch` in a second terminal so the stylesheet
rebuilds on save; `django-browser-reload` refreshes the page for you.

## Tasks (mise)

```sh
mise run dev        # runserver
mise run css        # build tailwind.css once
mise run watch      # rebuild the stylesheet on change
mise run test       # pytest
mise run lint       # ruff check
mise run typecheck  # pyright
mise run check      # all three
mise run resetdb    # drop, create, migrate
```

## Layout

```
config/         settings, root urls, health checks, context processors
users/          custom user model (e-mail as the identifier)
pages/          public marketing pages + sitemaps
shop/           products, orders, Stripe billing
templates/      base.html, error pages, allauth overrides
assets/css/     Tailwind source (source.css)
static/         favicon and the built stylesheet (generated)
tests/          pytest suite
```

## Endpoints worth knowing

| Path | Purpose |
| --- | --- |
| `/` | Index page (`pages.IndexView`) |
| `/shop/` | Product list; `/shop/<slug>/` for detail |
| `/shop/webhooks/stripe/` | Stripe webhook (CSRF-exempt, signature-verified) |
| `/accounts/…` | allauth (login, signup, e-mail verification) |
| `/healthz`, `/readyz` | Liveness and readiness probes |
| `/robots.txt`, `/sitemap.xml` | Crawler hints |

## E-mail

Local development prints e-mail to the console. Production uses SMTP and reads
`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`,
`EMAIL_USE_TLS` from the environment.

## Stripe

Set `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` and `STRIPE_WEBHOOK_SECRET`.
Locally, forward events with the Stripe CLI:

```sh
stripe listen --forward-to 127.0.0.1:8000/shop/webhooks/stripe/
```

A paid `checkout.session.completed` event flips the matching order to `paid`.

## Deployment (VPS)

`docker compose up -d --build` on the host. Caddy terminates TLS for
`$SITE_DOMAIN` and proxies to gunicorn; WhiteNoise serves the static files that
were collected during the image build. Required environment: `DJANGO_SECRET_KEY`,
`DJANGO_ALLOWED_HOSTS`, `DJANGO_SITE_URL`, `POSTGRES_PASSWORD`, `SITE_DOMAIN`,
the `EMAIL_*` block and the Stripe keys.
