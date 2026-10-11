"""Project settings for the in-memory SSR example.

Deliberately minimal: no database-backed apps, no migrations, no static
pipeline. ``DATABASES`` uses the dummy backend so that any accidental ORM
touch fails loudly instead of silently creating a database.

Templates use Django's built-in Jinja2 backend (see ``todos.jinja2`` for the
environment exposing URL reversing to templates).
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "django-insecure-ssr-memory-jinja-example-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

INSTALLED_APPS = [
    "todos",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [os.path.join(BASE_DIR, "todos", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "todos.jinja2.environment",
        },
    }
]

# Dummy backend: never touched. This example uses a process-local
# in-memory store (see todos.store) and must not use the ORM.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
