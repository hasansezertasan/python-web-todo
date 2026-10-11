"""Todo JSON API with Pycnic and in-memory storage."""

import os

from pycnic.core import WSGI, Handler

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


class TodoCollectionHandler(Handler):
    """Handles GET/POST /todos against one repository."""

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self.repo = repo

    def get(self):
        return [_to_json(todo) for todo in self.repo.list()]

    def post(self):
        title = self.request.data.get("title")
        if not _valid_title(title):
            # Pycnic ships no 422 error type, so set the status directly.
            self.response.status_code = 422
            return {"error": "title must be a non-empty string"}
        self.response.status_code = 201
        return _to_json(self.repo.create(title=title))


class TodoItemHandler(Handler):
    """Handles GET/PATCH/DELETE /todos/{id} against one repository."""

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self.repo = repo

    def get(self, todo_id: str):
        try:
            todo = self.repo.get(int(todo_id))
        except KeyError:
            self.response.status_code = 404
            return {"error": "Todo not found"}
        return _to_json(todo)

    def patch(self, todo_id: str):
        body = self.request.data
        if "title" in body and not _valid_title(body.get("title")):
            self.response.status_code = 422
            return {"error": "title must be a non-empty string"}
        try:
            todo = self.repo.update(
                int(todo_id), title=body.get("title"), done=body.get("done")
            )
        except KeyError:
            self.response.status_code = 404
            return {"error": "Todo not found"}
        return _to_json(todo)

    def delete(self, todo_id: str):
        try:
            self.repo.delete(int(todo_id))
        except KeyError:
            self.response.status_code = 404
            return {"error": "Todo not found"}
        self.response.status_code = 204
        return ""


def create_app(repo: InMemoryTodoRepository | None = None) -> type[WSGI]:
    """Build a fresh Pycnic WSGI app (a ``WSGI`` subclass) with its own store.

    Pycnic's WSGI callable is the subclass itself — each request
    instantiates it with ``(environ, start_response)`` — so the factory
    returns the class, not an instance.
    """
    repo = repo or InMemoryTodoRepository()

    class TodoApp(WSGI):
        routes = [
            ("/todos", TodoCollectionHandler(repo)),
            (r"/todos/([0-9]+)", TodoItemHandler(repo)),
        ]

    return TodoApp


app = create_app()


def main() -> None:
    from wsgiref.simple_server import make_server

    port = int(os.environ.get("PORT", "5000"))
    with make_server("0.0.0.0", port, app) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
