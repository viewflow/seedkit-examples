#!/bin/sh
set -eu

DB_DIR="${DB_DIR:-/app/db}"
DB_PATH="$DB_DIR/db.sqlite3"

mkdir -p "$DB_DIR"

if [ ! -f "$DB_PATH" ]; then
    echo "entrypoint: no database at $DB_PATH, attempting litestream restore"
    litestream restore -if-replica-exists -config /etc/litestream.yml "$DB_PATH"
fi

python manage.py migrate --noinput
python manage.py createcachetable --database cache

exec litestream replicate -config /etc/litestream.yml -exec \
    "gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile -"
