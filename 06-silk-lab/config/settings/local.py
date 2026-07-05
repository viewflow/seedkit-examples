from .base import *

if DEBUG:
    INSTALLED_APPS += ["silk"]
    # AFTER SecurityMiddleware, not before — prepending at index 0 routes
    # the profiler around Django's security headers on every request.
    sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(sec_idx + 1, "silk.middleware.SilkyMiddleware")

    INSTALLED_APPS += ["zeal"]
    MIDDLEWARE += ["zeal.middleware.zeal_middleware"]  # required to scope detection per request
    ZEAL_RAISE_ON_VIOLATION = True

    INSTALLED_APPS += ["django_migration_linter"]  # registers the `lintmigrations` command

    INSTALLED_APPS += ["django_extensions"]
