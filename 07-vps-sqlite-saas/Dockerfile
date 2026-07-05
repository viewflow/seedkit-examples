# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

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


FROM python:3.13-slim-trixie AS prod
ENV PATH="/opt/venv/bin:$PATH"

# v0.5.13 — check the latest tag on github.com/benbjohnson/litestream/releases.
RUN apt-get update && apt-get install -y --no-install-recommends wget \
 && ARCH=$(dpkg --print-architecture | sed 's/amd64/x86_64/') \
 && wget -q "https://github.com/benbjohnson/litestream/releases/download/v0.5.13/litestream-0.5.13-linux-${ARCH}.deb" \
 && dpkg -i "litestream-0.5.13-linux-${ARCH}.deb" \
 && rm "litestream-0.5.13-linux-${ARCH}.deb" \
 && rm -rf /var/lib/apt/lists/*
# Release assets name amd64 as x86_64 while arm64 keeps dpkg's name — the sed
# keeps the image building on M-series Macs too.

RUN groupadd --system django && useradd --system --gid django django

# Pre-create /data before `USER django` — the named volume mounts as root:root,
# so the django user can't write site.sqlite3 / cache.sqlite3 / WAL files otherwise.
RUN mkdir -p /data && chown django:django /data

# Pre-create /app/media for the same reason (media volume, WhiteNoise storage).
RUN mkdir -p /app/media && chown django:django /app/media

WORKDIR /app
COPY --from=builder --chown=django:django /opt/venv /opt/venv
COPY --from=builder --chown=django:django /app /app

# Bake the litestream config and entrypoint into the image at fixed paths.
# Bind-mounting `./litestream.yml` from `deploy/docker-compose.prod.yml` resolves
# against the compose-file directory and silently fails when the file lives at
# the project root.
COPY litestream.yml /etc/litestream.yml
COPY --chmod=755 entrypoint.sh /entrypoint.sh

USER django

ENTRYPOINT ["/entrypoint.sh"]
CMD []
