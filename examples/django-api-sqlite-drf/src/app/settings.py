"""Django settings for the django-api-sqlite-drf example."""

import os
from pathlib import Path

EXAMPLE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = "django-insecure-example-only-do-not-use-in-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "app",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # Overridable per test via the TODO_DB_PATH env var (see README).
        "NAME": os.environ.get("TODO_DB_PATH", str(EXAMPLE_DIR / "db.sqlite3")),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True

REST_FRAMEWORK = {
    # Maps serializer 400s to the contract's 422 (see views.py).
    "EXCEPTION_HANDLER": "app.views.api_exception_handler",
}
