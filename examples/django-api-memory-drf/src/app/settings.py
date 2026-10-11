"""Minimal Django settings. No ORM usage; DATABASES is a dummy never touched."""

SECRET_KEY = "django-insecure-dev-only-do-not-use-in-prod"

DEBUG = True

ALLOWED_HOSTS = ["*"]

ROOT_URLCONF = "app.urls"

APPEND_SLASH = False

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "app",
]

MIDDLEWARE = ["django.middleware.common.CommonMiddleware"]

# Dummy setting required by Django at startup. Never touched: this example
# has no models, no migrations, and issues no ORM queries.
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {"UNAUTHENTICATED_USER": None}
