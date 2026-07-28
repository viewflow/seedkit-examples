# Builder: install dependencies and build static assets with uv.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY . .

# Build Tailwind CSS and collect static files; SECRET_KEY is a build-time dummy,
# nothing here touches the database.
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-only-dummy-key \
    uv run --no-sync manage.py tailwind build && \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-only-dummy-key \
    uv run --no-sync manage.py collectstatic --noinput

# Runtime: slim image with just the app and its virtualenv.
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

USER app
EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
