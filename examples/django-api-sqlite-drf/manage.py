#!/usr/bin/env python
"""Django management script (framework-mandated root file).

Only wires src/ onto sys.path, then delegates to Django. Tables are migrated
automatically before `runserver` starts (see README).
"""

import os
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")


def main() -> None:
    import django
    from django.core.management import call_command, execute_from_command_line

    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        django.setup()
        call_command("migrate", run_syncdb=True, verbosity=0)
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
