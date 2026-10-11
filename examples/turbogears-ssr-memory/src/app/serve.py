"""Waitress entry point: ``turbogears-ssr-memory`` (see pyproject scripts)."""

import os

from waitress import serve

from .main import create_app


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    serve(create_app(), host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
