"""Waitress entry point: ``pyramid-ssr-memory`` (see pyproject scripts)."""

from waitress import serve

from .main import create_app


def main() -> None:
    serve(create_app(), host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
