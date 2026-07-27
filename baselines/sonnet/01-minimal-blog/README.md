# 01-minimal-blog

A tiny Django blog to verify the scaffolding skill works end-to-end.

## Setup

```sh
cp .env.example .env
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the post list and
`http://127.0.0.1:8000/admin/` for the admin site.

## Tests

```sh
uv run manage.py test
```

See `AGENTS.md` for stack details and conventions.
