from .base import *  # noqa: F403
from .base import env

DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

INSTALLED_APPS += ["zeal"]  # noqa: F405
MIDDLEWARE += ["zeal.middleware.zeal_middleware"]  # noqa: F405
