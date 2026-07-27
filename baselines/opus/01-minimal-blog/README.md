# 01-minimal-blog

A tiny Django blog — posts, an admin to write them in, and a public list and
detail page. It exists to verify the scaffold works end to end.

## Requirements

- [uv](https://docs.astral.sh/uv/) (manages Python and dependencies)

## Getting started

```sh
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

- Blog: <http://127.0.0.1:8000/>
- Admin: <http://127.0.0.1:8000/admin/>

Write a post in the admin. A post is public once `published_at` is set to a
past date; leave it empty to keep the post a draft.

## Tests

```sh
uv run manage.py test
```

## Configuration

Configuration comes from environment variables, optionally via a `.env` file
(gitignored). Copy `.env.example` to `.env` to start. Every setting has a
local-dev default, so the project boots without one.

| Variable | Default | Notes |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | insecure dev key | Set a real one outside local dev. |
| `DJANGO_DEBUG` | `True` | This project has no production config. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | Comma-separated. |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | |
| `EMAIL_URL` | `consolemail://` | Mail is printed to stdout. |
| `DEFAULT_FROM_EMAIL` | `noreply@localhost` | |

## Scope

No linter, type checker, pre-commit, i18n, custom user model, REST API,
frontend build, or deployment setup — this is the bare floor on purpose.
