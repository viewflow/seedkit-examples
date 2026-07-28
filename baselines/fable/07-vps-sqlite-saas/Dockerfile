# syntax=docker/dockerfile:1

# --- Builder: install dependencies into a project-local virtualenv ---
FROM python:3.14-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

# --- Prod: runtime image with Litestream ---
FROM python:3.14-slim AS prod

ARG TARGETARCH
ARG LITESTREAM_VERSION=v0.3.13

ADD https://github.com/benbjohnson/litestream/releases/download/${LITESTREAM_VERSION}/litestream-${LITESTREAM_VERSION}-linux-${TARGETARCH}.deb /tmp/litestream.deb
RUN dpkg -i /tmp/litestream.deb && rm /tmp/litestream.deb

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    SQLITE_DIR=/app/data \
    MEDIA_ROOT=/app/media

RUN groupadd --system django && useradd --system --gid django --home-dir /app django

WORKDIR /app

COPY --from=builder --chown=django:django /app /app
COPY litestream.yml /etc/litestream.yml

# Collect static assets into the image (served by WhiteNoise).
RUN DJANGO_SECRET_KEY=build-only-placeholder DJANGO_ALLOWED_HOSTS=* \
    python manage.py collectstatic --noinput \
    && mkdir -p /app/data /app/media \
    && chown -R django:django /app/data /app/media /app/staticfiles

USER django

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
