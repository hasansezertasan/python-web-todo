"""Todo JSON API with Tornado and in-memory storage."""

import os

import tornado.ioloop
import tornado.web

from .handlers import TodoDetailHandler, TodoListHandler
from .store import TodoStore


def create_app(store: TodoStore | None = None) -> tornado.web.Application:
    """Return a fresh application with its own empty store (unless given)."""
    return tornado.web.Application(
        [(r"/todos", TodoListHandler), (r"/todos/([0-9]+)", TodoDetailHandler)],
        store=store or TodoStore(),
    )


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
