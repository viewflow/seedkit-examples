# 01-minimal-blog

A tiny Django blog. Deliberately bare: no linter, no type checker, no
pre-commit, no i18n, no custom user model, no API, no frontend build.

## Layout

```
config/          settings.py (single file), urls.py, wsgi.py, asgi.py
blog/            Post model, class-based list/detail views, admin, tests
templates/       base.html + blog/*.html (project-level, not app-level)
static/          empty; STATICFILES_DIRS points here
```

## Commands

Everything runs through `uv` — no manual venv activation.

```sh
uv sync                            # install deps
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver         # http://127.0.0.1:8000/
uv run manage.py test              # stock Django test runner
uv run manage.py makemigrations    # after model changes
```

## Conventions

- Settings read the environment via `django-environ`; `.env` is optional and
  gitignored. Defaults in `config/settings.py` are tuned for local dev, so a
  fresh clone boots with no `.env` at all.
- `DEBUG` defaults to **True**. This project has no production configuration
  by design — set `DJANGO_DEBUG=False` and a real `DJANGO_SECRET_KEY` before
  running it anywhere but a laptop.
- Email uses `EMAIL_URL` (`consolemail://` by default), expanded through
  `env.email_url()`. Mail is printed to stdout.
- Drafts are `Post.published_at = NULL`. Public views only ever query
  `Post.objects.published()`, so drafts and future-dated posts 404.
- Tests live in `blog/tests.py` and use `TestCase` + the test client. Add
  tests next to the app they cover; there is no separate `tests/` package.
