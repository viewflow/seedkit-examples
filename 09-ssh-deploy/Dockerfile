# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

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

# DJANGO_DEBUG=True unlocks dev defaults so collectstatic boots without
# real SECRET_KEY / DATABASE_URL. SETTINGS_MODULE → production so STORAGES
# (manifest static storage) applies; otherwise manage.py uses local.py.
RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DEBUG=True \
    /opt/venv/bin/python manage.py collectstatic --noinput


FROM python:3.12-slim-bookworm AS prod
# HOME points at the app dir (owned by django below) — the system user has no
# home directory of its own, and gunicorn 26's control server writes a socket
# under $HOME on boot; without this it logs "Permission denied: '/home/django'"
# on every start.
ENV PATH="/opt/venv/bin:$PATH" \
    HOME="/app"

# postgresql-client ships pg_dump / pg_isready for django-dbbackup and
# ad-hoc shell debugging. Bookworm's stock `postgresql-client` meta-package
# resolves to major 15, but the `postgres:17` image used in
# deploy/docker-compose.prod.yml needs a matching-or-newer client or pg_dump
# aborts with "server version mismatch" — pull client 17 from the PGDG apt
# repo instead of the Debian default.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl -fsSL -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc \
        https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends postgresql-client-17 \
    && apt-get purge -y --auto-remove curl gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

ARG GIT_SHA=unknown
ENV GIT_SHA=${GIT_SHA}

USER django

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000"]
