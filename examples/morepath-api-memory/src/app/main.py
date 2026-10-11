"""Todo JSON API with Morepath and in-memory storage."""

import json
import os

import morepath
from morepath import Response
from webob import exc as wexc

from .models import Todo, TodoCollection
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _request_body(request: morepath.Request) -> dict:
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except (ValueError, UnicodeDecodeError):
        return {}
    return body if isinstance(body, dict) else {}


def _error(status: int, message: str) -> Response:
    return Response(json_body={"error": message}, status=status)


def create_app(repo: InMemoryTodoRepository | None = None) -> morepath.App:
    """Build a fresh Morepath WSGI app with its own empty store.

    Morepath binds `@path`/`@view` configuration to the app class at
    commit time, so each call creates a new `App` subclass, registers the
    models and views against it (closing over this call's `repo`), and
    commits it with `morepath.commit`. Tests therefore get a fully
    isolated app + store per call; pass `repo` explicitly to share one.
    """
    repo = repo or InMemoryTodoRepository()

    class TodoApp(morepath.App):
        pass

    @TodoApp.path(model=TodoCollection, path="todos")
    def _get_collection() -> TodoCollection:
        return TodoCollection(repo)

    @TodoApp.path(model=Todo, path="todos/{todo_id}")
    def _get_todo(todo_id: str) -> Todo | None:
        try:
            return repo.get(int(todo_id))
        except (KeyError, ValueError):
            # Unknown (or non-integer) id: unmatched model, so Morepath
            # raises HTTPNotFound, rendered as JSON by _not_found below.
            return None

    @TodoApp.json(model=TodoCollection)
    def _list_todos(self: TodoCollection, request: morepath.Request) -> list[dict]:
        return [_to_json(todo) for todo in repo.list()]

    @TodoApp.json(model=TodoCollection, request_method="POST")
    def _create_todo(
        self: TodoCollection, request: morepath.Request
    ) -> Response | dict:
        title = _request_body(request).get("title")
        if not _valid_title(title):
            return _error(422, "title must be a non-empty string")
        return Response(json_body=_to_json(repo.create(title=title)), status=201)

    @TodoApp.json(model=Todo)
    def _get_todo_view(self: Todo, request: morepath.Request) -> dict:
        return _to_json(self)

    @TodoApp.json(model=Todo, request_method="PATCH")
    def _update_todo(self: Todo, request: morepath.Request) -> Response | dict:
        body = _request_body(request)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return _error(422, "title must be a non-empty string")
        if done is not None and not isinstance(done, bool):
            return _error(422, "done must be a boolean")
        return _to_json(repo.update(self.id, title=title, done=done))

    @TodoApp.view(model=Todo, request_method="DELETE")
    def _delete_todo(self: Todo, request: morepath.Request) -> Response:
        repo.delete(self.id)
        return Response(status=204)

    @TodoApp.json(model=wexc.HTTPNotFound)
    def _not_found(self: wexc.HTTPNotFound, request: morepath.Request) -> Response:
        # Morepath's default 404 for unmatched paths/models is plain text;
        # the contract requires a JSON body, so re-render it as JSON.
        return _error(404, "Todo not found")

    morepath.commit(TodoApp)
    return TodoApp()


app = create_app()


def main() -> None:
    from wsgiref.simple_server import make_server

    port = int(os.environ.get("PORT", "5000"))
    with make_server("0.0.0.0", port, app) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
