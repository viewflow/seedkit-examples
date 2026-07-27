# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN uv sync --frozen --no-dev

# Build-time only settings so collectstatic/tailwind build don't need real secrets.
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    DJANGO_SECRET_KEY=build-time-only \
    DJANGO_ALLOWED_HOSTS=localhost \
    EMAIL_HOST=localhost

RUN uv run manage.py tailwind build \
    && uv run manage.py collectstatic --noinput

FROM python:3.12-slim-bookworm AS runtime

RUN groupadd --system app && useradd --system --gid app app

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

COPY --from=builder --chown=app:app /app /app

USER app

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
