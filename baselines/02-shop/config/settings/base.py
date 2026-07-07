"""
Django settings for the shop project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="django-insecure-change-me-in-production")

DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])  # pyright: ignore[reportArgumentType]


# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]

THIRD_PARTY_APPS = [
    "django_tailwind_cli",
    "allauth",
    "allauth.account",
    "axes",
]

LOCAL_APPS = [
    "users",
    "pages",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DEFAULT_DATABASE_URL = "postgres://postgres:postgres@localhost:5432/shop_db"

DATABASES = {
    "default": env.db("DATABASE_URL", default=DEFAULT_DATABASE_URL),  # pyright: ignore[reportArgumentType]
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "users.User"


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = 1

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "pages:index"
LOGOUT_REDIRECT_URL = "pages:index"


# django-allauth
# https://docs.allauth.org/en/latest/account/configuration.html

ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m",
}


# django-axes
# https://django-axes.readthedocs.io/en/latest/4_configuration.html

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # hours
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]


# django-tailwind-cli
# https://django-tailwind-cli.readthedocs.io/

TAILWIND_CLI_USE_DAISY_UI = True
TAILWIND_CLI_SRC_CSS = BASE_DIR / "static/css/input.css"
TAILWIND_CLI_DIST_CSS = "css/tailwind.css"


# Email
# https://docs.djangoproject.com/en/5.1/topics/email/

EMAIL_BACKEND = env.str(
    "DJANGO_EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = env.str("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
SERVER_EMAIL = env.str("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)


# Stripe
# https://docs.stripe.com/api

STRIPE_PUBLISHABLE_KEY = env.str("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = env.str("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env.str("STRIPE_WEBHOOK_SECRET", default="")
