from .base import *

if DEBUG:
    INSTALLED_APPS += ["django_extensions"]

    INSTALLED_APPS += ["silk"]
    # AFTER SecurityMiddleware, not before. Prepending at index 0 routes
    # the profiler around Django's security headers on every request.
    sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")
    MIDDLEWARE.insert(sec_idx + 1, "silk.middleware.SilkyMiddleware")

    INSTALLED_APPS += ["zeal"]
    MIDDLEWARE += ["zeal.middleware.zeal_middleware"]
    ZEAL_RAISE_ON_VIOLATION = True

    INSTALLED_APPS += ["django_migration_linter"]
