#!/usr/bin/env python
"""Django's command-line utility (framework-mandated at the example root)."""

import os
import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Install dependencies first, e.g. "
            "`uv sync --project examples/django-ssr-memory-jinja` "
            "or `uv run --project examples/django-ssr-memory-jinja ...`."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
