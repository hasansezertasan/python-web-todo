"""Testable entry point: create_app() with optional DB-path override."""

import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent


def create_app(db_path=None):
    """Configure Django, migrate, and return the WSGI application.

    Pass ``db_path`` (or set ``TODO_DB_PATH``) to point SQLite at a fresh
    file per test. Migrations run automatically via ``run_syncdb`` — no
    migration files are shipped.
    """
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    if db_path is not None:
        os.environ["TODO_DB_PATH"] = str(db_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

    import django
    from django.apps import apps

    if not apps.ready:
        django.setup()

    if db_path is not None:
        from django.conf import settings as dj_settings
        from django.db import connections

        dj_settings.DATABASES["default"]["NAME"] = str(db_path)
        connections.close_all()

    from django.core.management import call_command

    call_command("migrate", run_syncdb=True, verbosity=0)

    from django.core.handlers.wsgi import WSGIHandler

    return WSGIHandler()


def main() -> None:
    create_app()
    from django.core.management import call_command

    call_command("runserver", "8000")


if __name__ == "__main__":
    main()
