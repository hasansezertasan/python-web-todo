#!/usr/bin/env python
"""Django's command-line utility (framework-mandated at the example root)."""

import os
import sys


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(base_dir, "src"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Install dependencies first, e.g. "
            "`uv sync --project examples/django-ssr-memory-native` "
            "or `uv run --project examples/django-ssr-memory-native ...`."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
