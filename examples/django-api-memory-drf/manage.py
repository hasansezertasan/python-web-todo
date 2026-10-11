#!/usr/bin/env python
"""Django management entry point (framework-mandated file at the example root)."""

import os
import sys


def main() -> None:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed. From this directory run `uv sync` first."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
