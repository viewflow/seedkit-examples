# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12-slim
ARG LITESTREAM_VERSION=0.5.13

FROM python:${PYTHON_VERSION} AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev --no-editable

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-editable

RUN DJANGO_SECRET_KEY=build-time-only \
    uv run --no-sync python manage.py collectstatic --noinput --settings=config.settings.production


FROM python:${PYTHON_VERSION} AS prod

ARG LITESTREAM_VERSION

RUN apt-get update && apt-get install --no-install-recommends -y curl ca-certificates \
    && ARCH="$(dpkg --print-architecture)" \
    && case "${ARCH}" in \
         amd64) LITESTREAM_ARCH=x86_64 ;; \
         arm64) LITESTREAM_ARCH=arm64 ;; \
         *) echo "unsupported architecture: ${ARCH}" && exit 1 ;; \
       esac \
    && curl -fsSL -o /tmp/litestream.deb \
         "https://github.com/benbjohnson/litestream/releases/download/v${LITESTREAM_VERSION}/litestream-${LITESTREAM_VERSION}-linux-${LITESTREAM_ARCH}.deb" \
    && dpkg -i /tmp/litestream.deb \
    && rm /tmp/litestream.deb \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system app && useradd --system --gid app --home-dir /app app

WORKDIR /app

COPY --from=builder --chown=app:app /app /app
COPY --chown=app:app litestream.yml /etc/litestream.yml
COPY --chown=app:app entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PYTHONUNBUFFERED=1

RUN mkdir -p /app/data /app/media && chown -R app:app /app/data /app/media

USER app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
