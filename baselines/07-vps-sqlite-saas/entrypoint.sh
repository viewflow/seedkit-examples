#!/bin/sh
set -eu

DB_PATH="${DJANGO_DB_PATH:-/app/data/db.sqlite3}"

mkdir -p "$(dirname "$DB_PATH")"

if [ ! -f "$DB_PATH" ] && [ -n "${LITESTREAM_S3_BUCKET:-}" ]; then
    echo "entrypoint: no local database at $DB_PATH, attempting litestream restore..."
    litestream restore -if-replica-exists "$DB_PATH"
fi

echo "entrypoint: running migrations..."
python manage.py migrate --noinput
python manage.py createcachetable --database=cache

echo "entrypoint: starting litestream replication + app..."
exec litestream replicate -exec "$*"
