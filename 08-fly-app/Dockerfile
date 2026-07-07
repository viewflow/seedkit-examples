# syntax=docker/dockerfile:1

# django-bolt ships no manylinux wheel for linux/aarch64 — pin the build to
# linux/amd64 (via emulation on Apple Silicon hosts) so uv installs the
# published manylinux2014_x86_64 wheel instead of compiling the Rust
# extension from source at build time.
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

# collectstatic runs at deploy time, not build time — this project uses S3
# storage, and collectstatic needs real bucket creds that must not enter
# the build context. See fly.toml's release_command.


FROM --platform=linux/amd64 python:3.12-slim-bookworm AS prod
ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

USER django

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]
