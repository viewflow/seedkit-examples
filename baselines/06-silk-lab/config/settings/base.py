"""
Django settings for config project.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str(
    "SECRET_KEY",
    default="django-insecure-zq^8d9s0q*fp&$9_@vl%=!dnp&z!wp7byy!6+hzg%0i#$1x#mx",
)

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "django_migration_linter",
    "django_tasks",
    "django_tasks_db",
    "silk",
    "jobs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "silk.middleware.SilkyMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.analytics",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="postgres:///silk_db",
    )
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/
# i18n is not used in this project.

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Email
# https://docs.djangoproject.com/en/6.0/topics/email/

vars().update(env.email_url("EMAIL_URL", default="consolemail://"))


# Django Tasks (django-tasks-db) — background jobs on the database backend
# https://github.com/RealOrangeOne/django-tasks

TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.backend.DatabaseBackend",
    }
}


# django-migration-linter
# https://github.com/3YOURMIND/django-migration-linter

MIGRATION_LINTER_OPTIONS = {
    "database": "default",
    # Third-party migration histories we don't control and can't rewrite.
    "exclude_apps": ["silk", "django_tasks_database"],
}


# GoatCounter analytics (self-hosted, env-driven site code)
# https://www.goatcounter.com/help/countscript

GOATCOUNTER_SITE_CODE = env.str("GOATCOUNTER_SITE_CODE", default="")
