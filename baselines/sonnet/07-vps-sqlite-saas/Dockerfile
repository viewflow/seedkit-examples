# syntax=docker/dockerfile:1

FROM python:3.12-slim-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev

# Dummy build-time settings so `collectstatic` can import config.settings.production
# without requiring real secrets. Nothing here touches the database.
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-time-placeholder-not-used-at-runtime \
    EMAIL_URL=consolemail://build \
    ALLOWED_HOSTS=localhost
RUN uv run manage.py collectstatic --noinput


FROM python:3.12-slim-bookworm AS prod

ARG TARGETARCH
ARG LITESTREAM_VERSION=0.3.13

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl ca-certificates; \
    curl -fsSL -o /tmp/litestream.deb \
        "https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-v${LITESTREAM_VERSION}-linux-${TARGETARCH}.deb"; \
    dpkg -i /tmp/litestream.deb; \
    rm /tmp/litestream.deb; \
    apt-get purge -y curl; \
    apt-get autoremove -y; \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django --create-home --home-dir /app django

WORKDIR /app
COPY --from=builder --chown=django:django /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    DB_DIR=/app/db

COPY --chown=django:django litestream.yml /etc/litestream.yml
COPY --chown=django:django entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && mkdir -p /app/db /app/media && chown -R django:django /app/db /app/media

USER django

EXPOSE 8000

CMD ["/entrypoint.sh"]
