# 01-minimal-blog

A tiny Django blog to verify the skill works end-to-end.

## Quick start

```sh
uv sync
cp .env.example .env
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Then open <http://127.0.0.1:8000/admin/> and manage blog posts there.

## Tests

```sh
uv run manage.py test
```

See [AGENTS.md](AGENTS.md) for the project conventions.
