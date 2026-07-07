"""Base settings, shared by every environment."""

from pathlib import Path

import environ
import structlog

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env.str('DJANGO_SECRET_KEY')
DEBUG = env.bool('DJANGO_DEBUG', default=False)
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'corsheaders',
    'storages',
    'django_structlog',
    'django_tasks',
    'django_tasks_rq',
    'django_rq',
    'core',
    'jobs',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_structlog.middlewares.RequestMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='postgres://media_vault:media_vault@127.0.0.1:5432/media_vault',
    ),
}

# Redis (shared by the channel layer, the task queue and django-rq)

REDIS_URL = env.str('REDIS_URL', default='redis://127.0.0.1:6379/0')

# Real-time channel layer

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}

# Background tasks (Django Tasks, RQ backend)

TASKS = {
    'default': {
        'BACKEND': 'django_tasks_rq.RQBackend',
        'QUEUES': ['default'],
    },
}

RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL,
        'DEFAULT_TIMEOUT': 360,
    },
}

RQ = {
    'JOB_CLASS': 'django_tasks_rq.Job',
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = True

# Static files

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email

EMAIL_CONFIG = env.email_url('EMAIL_URL', default='consolemail://')
vars().update(EMAIL_CONFIG)

# S3-compatible object storage (MinIO locally, any S3-compatible provider in prod)

AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID', default='minioadmin')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY', default='minioadmin')
AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME', default='media-vault')
AWS_S3_ENDPOINT_URL = env.str('AWS_S3_ENDPOINT_URL', default='http://127.0.0.1:9000')
AWS_S3_REGION_NAME = env.str('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_ADDRESSING_STYLE = 'path'
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = env.bool('AWS_QUERYSTRING_AUTH', default=True)

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

# CORS

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Structured logging (structlog): pretty console renderer in dev, JSON in prod.

structlog_shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.TimeStamper(fmt='iso'),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
]

structlog.configure(
    processors=structlog_shared_processors
    + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processors': [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
            'foreign_pre_chain': structlog_shared_processors,
        },
        'console': {
            '()': structlog.stdlib.ProcessorFormatter,
            'processors': [
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(),
            ],
            'foreign_pre_chain': structlog_shared_processors,
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console' if DEBUG else 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': env.str('DJANGO_LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django_structlog': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
