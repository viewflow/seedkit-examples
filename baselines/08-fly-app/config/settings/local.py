"""Local development settings: runserver against Postgres/Redis/MinIO in docker-compose."""

from .base import *  # noqa: F403
from .base import env

DEBUG = True

ALLOWED_HOSTS = ["*"]

# MinIO (S3-compatible) running locally via docker-compose.
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", default="http://127.0.0.1:9000")
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="minioadmin")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="minioadmin")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default="fly-app")
AWS_S3_URL_PROTOCOL = "http:"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
