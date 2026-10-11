"""Todo JSON API with CherryPy and in-memory storage."""

import json
import os

import cherrypy

from .models import Todo
from .repository import InMemoryTodoRepository

# Dispatch config shared by the WSGI app factory and the standalone server.
_DISPATCH_CONFIG = {
    "/": {"request.dispatch": cherrypy.dispatch.MethodDispatcher()},
}


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _request_body() -> dict:
    body = getattr(cherrypy.request, "json", None)
    return body if isinstance(body, dict) else {}


def _error(message: str, status: int) -> dict:
    cherrypy.response.status = status
    return {"error": message}


def _raw_error(message: str, status: int) -> bytes:
    # DELETE carries no tools.json_out (a 204 must have no body), so its
    # errors are serialized by hand instead. CherryPy page handlers must
    # return bytes once json_out is out of the picture.
    cherrypy.response.status = status
    cherrypy.response.headers["Content-Type"] = "application/json"
    return json.dumps({"error": message}).encode("utf-8")


class TodoResource:
    """Single resource mounted at /todos.

    MethodDispatcher (the idiomatic CherryPy way to serve REST) maps HTTP
    verbs onto same-named methods of one exposed object; leftover path
    segments arrive as positional args, so GET serves both the collection
    (/todos) and a single member (/todos/{id}).
    """

    exposed = True

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self._repo = repo

    @cherrypy.tools.json_out()
    def GET(self, todo_id: str | None = None, *extra: str) -> object:
        if extra:
            return _error("Todo not found", 404)
        if todo_id is None:
            return [_to_json(todo) for todo in self._repo.list()]
        try:
            todo = self._repo.get(int(todo_id))
        except (ValueError, KeyError):
            return _error("Todo not found", 404)
        return _to_json(todo)

    @cherrypy.tools.json_in(force=False)
    @cherrypy.tools.json_out()
    def POST(self, todo_id: str | None = None, *extra: str) -> object:
        if todo_id is not None or extra:
            return _error("Todo not found", 404)
        title = _request_body().get("title")
        if not _valid_title(title):
            return _error("title must be a non-empty string", 422)
        cherrypy.response.status = 201
        return _to_json(self._repo.create(title=title))

    @cherrypy.tools.json_in(force=False)
    @cherrypy.tools.json_out()
    def PATCH(self, todo_id: str | None = None, *extra: str) -> object:
        if todo_id is None or extra:
            return _error("Todo not found", 404)
        body = _request_body()
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return _error("title must be a non-empty string", 422)
        try:
            todo = self._repo.update(int(todo_id), title=title, done=done)
        except (ValueError, KeyError):
            return _error("Todo not found", 404)
        return _to_json(todo)

    def DELETE(self, todo_id: str | None = None, *extra: str) -> bytes:
        if todo_id is None or extra:
            return _raw_error("Todo not found", 404)
        try:
            self._repo.delete(int(todo_id))
        except (ValueError, KeyError):
            return _raw_error("Todo not found", 404)
        cherrypy.response.status = 204
        cherrypy.response.headers.pop("Content-Type", None)
        return b""


def create_app(
    repo: InMemoryTodoRepository | None = None,
) -> cherrypy.Application:
    """Build a fresh, independently-mounted WSGI app with its own store."""
    resource = TodoResource(repo or InMemoryTodoRepository())
    return cherrypy.Application(resource, "/todos", _DISPATCH_CONFIG)


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "5000"))
    cherrypy.config.update(
        {"server.socket_host": "0.0.0.0", "server.socket_port": port}
    )
    cherrypy.tree.mount(app.root, "/todos", _DISPATCH_CONFIG)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == "__main__":
    main()
