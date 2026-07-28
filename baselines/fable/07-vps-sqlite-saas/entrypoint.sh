#!/bin/sh
set -eu

DB_PATH="${SQLITE_DIR:-/app/data}/db.sqlite3"

# Restore the database from the replica if this is a fresh volume.
if [ ! -f "$DB_PATH" ]; then
    echo "Database not found, attempting Litestream restore..."
    litestream restore -if-replica-exists -config /etc/litestream.yml "$DB_PATH"
fi

python manage.py migrate --noinput
python manage.py createcachetable --database cache

# Replicate continuously while gunicorn serves the app.
exec litestream replicate -config /etc/litestream.yml \
    -exec "gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 --access-logfile - --error-logfile -"
