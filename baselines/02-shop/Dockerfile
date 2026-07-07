#############################################
# Builder: resolve deps and build static assets
#############################################
FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Placeholder settings so build-time management commands don't need real secrets.
ENV DJANGO_SETTINGS_MODULE=config.settings.production \
    DJANGO_SECRET_KEY=build-time-placeholder \
    DJANGO_ALLOWED_HOSTS=localhost \
    DATABASE_URL=postgres://user:pass@localhost:5432/placeholder

RUN uv run python manage.py tailwind build \
    && uv run python manage.py collectstatic --noinput


#############################################
# Runtime
#############################################
FROM python:3.12-slim-bookworm AS runtime

RUN groupadd --system app && useradd --system --gid app --create-home app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/staticfiles /app/staticfiles
COPY --chown=app:app . .

USER app

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
