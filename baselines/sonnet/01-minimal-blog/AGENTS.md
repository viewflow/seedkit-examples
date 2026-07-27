# Agent notes

- Settings live in `config/settings.py` (single file, no split by environment).
- Config comes from `.env` (see `.env.example`) via django-environ.
- Database: SQLite, file `db.sqlite3`, not committed.
- Test runner: stock `manage.py test` (`uv run manage.py test`).
- No linter, no type checker, no i18n, no custom user model configured.
- Email backend is derived from `EMAIL_URL` (console backend by default).
