# 01 Minimal Blog

A tiny Django blog to verify the skill works end-to-end.

## Stack

- Django 5.1, SQLite
- Single-file settings (`config/settings.py`), config via `.env` (django-environ)
- Stock `manage.py test` test runner
- Console email backend

## Setup

```sh
cp .env.example .env
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

Visit http://127.0.0.1:8000/ for the post list and http://127.0.0.1:8000/admin/ for the admin.

## Tests

```sh
uv run manage.py test
```
