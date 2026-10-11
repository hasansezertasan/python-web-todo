"""Project settings for the in-memory SSR example.

Deliberately minimal: no database-backed apps, no migrations, no static
pipeline. ``DATABASES`` uses the dummy backend so that any accidental ORM
touch fails loudly instead of silently creating a database.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-ssr-memory-native-example-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

INSTALLED_APPS = ["todos"]

MIDDLEWARE = ["django.middleware.common.CommonMiddleware"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "todos" / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {},
    }
]

# Dummy backend: never touched. This example uses a process-local
# in-memory store (see todos.store) and must not use the ORM.
DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
