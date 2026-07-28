FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

# `uv` drives dependency management; the venv lives in the workspace so the
# editor's interpreter path is stable.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/workspace/.venv \
    PYTHONUNBUFFERED=1

# libpq for psycopg, plus the postgres/redis clients for poking at the services.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 postgresql-client redis-tools \
    && rm -rf /var/lib/apt/lists/*
