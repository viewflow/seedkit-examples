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
# real SECRET_KEY / DATABASE_URL. SETTINGS_MODULE -> production so STORAGES
# (manifest static storage, once wired) and other prod-only blocks import
# cleanly at build time.
RUN DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_DEBUG=True \
    /opt/venv/bin/python manage.py collectstatic --noinput


FROM python:3.12-slim-bookworm AS prod
ENV PATH="/opt/venv/bin:$PATH"

# postgresql-client ships pg_dump / pg_isready for django-dbbackup and
# ad-hoc shell debugging. Bookworm's default apt repo only carries the
# major-15 client — add the PGDG repo to get major 17, matching the
# `postgres:17` image; a mismatched client aborts pg_dump with
# "server version mismatch".
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates \
    && install -d /usr/share/postgresql-common/pgdg \
    && wget --quiet -O /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends postgresql-client-17 \
    && apt-get purge -y --auto-remove wget gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system django && useradd --system --gid django django

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

USER django

ARG GIT_SHA=unknown
ENV SENTRY_RELEASE=${GIT_SHA}

CMD ["gunicorn", "config.wsgi", "--bind", "0.0.0.0:8000", "--max-requests", "1000", "--max-requests-jitter", "100", "--access-logfile", "-"]
