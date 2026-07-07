from .base import *  # noqa: F403
from .base import INSTALLED_APPS, MIDDLEWARE, env

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# django-zeal: catch N+1 queries during local development.
# Not recommended in production — see https://github.com/taobojlen/django-zeal
INSTALLED_APPS = [*INSTALLED_APPS, "zeal"]
MIDDLEWARE = [*MIDDLEWARE, "zeal.middleware.zeal_middleware"]
