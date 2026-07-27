class CacheRouter:
    """Route the cache table (django_cache app) to the dedicated cache.sqlite3 database."""

    route_app_labels = {"django_cache"}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "cache"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return "cache"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == "cache"
        if db == "cache":
            return False
        return None
