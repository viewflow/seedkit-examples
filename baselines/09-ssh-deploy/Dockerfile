# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev


FROM python:3.12-slim-bookworm AS runtime

RUN groupadd --system app && useradd --system --create-home --gid app app

RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

RUN mkdir -p /app/staticfiles /app/backups && chown app:app /app/staticfiles /app/backups

USER app

RUN DJANGO_SECRET_KEY=build DJANGO_ALLOWED_HOSTS=localhost \
    DATABASE_URL=sqlite:///build.sqlite3 \
    python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
