"""Todo JSON API with circuits.web and in-memory storage."""

import os

from circuits.web import Server

from .controllers import TodosController
from .repository import InMemoryTodoRepository


def create_app(
    store: InMemoryTodoRepository | None = None,
    host: str = "0.0.0.0",
    port: int = 8000,
) -> Server:
    """Build (and bind) a fresh server with its own empty store.

    circuits has no separate app object: the ``Server`` component *is*
    the application, so the factory returns a bound ``Server`` with a
    ``TodosController`` registered. Call ``.run()`` on it to serve.
    Each process (and each factory call with a fresh store) starts empty.
    """
    server = Server((host, port))
    TodosController(store or InMemoryTodoRepository()).register(server)
    return server


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    create_app(port=port).run()


if __name__ == "__main__":
    main()
