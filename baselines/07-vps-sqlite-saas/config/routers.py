class CacheRouter:
    """Route the cache table's queries to the dedicated cache.sqlite3 database."""

    cache_app = "django_cache"
    cache_db = "cache"

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.cache_app:
            return self.cache_db
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.cache_app:
            return self.cache_db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.cache_app:
            return db == self.cache_db
        if db == self.cache_db:
            return False
        return None
