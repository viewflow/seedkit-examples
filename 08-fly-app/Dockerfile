# syntax=docker/dockerfile:1
# Pinned to linux/amd64: django-bolt ships a precompiled Rust extension and
# Fly's default machines are amd64 — building natively on an Apple Silicon
# host would otherwise produce a builder/runtime arch mismatch.
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# collectstatic is NOT run at build time — storage is S3 (MinIO/real S3),
# and collectstatic needs real bucket creds at deploy time, not build time.
# See fly.toml's release_command.


FROM --platform=linux/amd64 python:3.12-slim-bookworm AS prod
ENV PATH="/opt/venv/bin:$PATH"

ARG GIT_SHA=unknown
ENV SENTRY_RELEASE=${GIT_SHA}

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

USER django

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--max-requests", "1000", "--max-requests-jitter", "100", "--access-logfile", "-"]
