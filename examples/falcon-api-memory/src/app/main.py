"""Todo JSON API with Falcon (WSGI) and in-memory storage."""

import falcon

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _request_json(req: falcon.Request) -> dict:
    """Return the JSON object body, or {} when absent, malformed, or not an object."""
    try:
        body = req.media
    except falcon.HTTPError:
        # No body (MediaNotFoundError) or unparseable body (MediaMalformedError).
        return {}
    return body if isinstance(body, dict) else {}


def _error(resp: falcon.Response, status: str, message: str) -> None:
    # Explicit JSON error bodies; do not rely on Falcon's default error rendering.
    resp.status = status
    resp.media = {"error": message}


class TodoCollectionResource:
    """Resource for GET /todos and POST /todos."""

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self._repo = repo

    def on_get(self, _req: falcon.Request, resp: falcon.Response) -> None:
        resp.media = [_to_json(todo) for todo in self._repo.list()]

    def on_post(self, req: falcon.Request, resp: falcon.Response) -> None:
        title = _request_json(req).get("title")
        if not _valid_title(title):
            _error(resp, falcon.HTTP_422, "title must be a non-empty string")
            return
        resp.status = falcon.HTTP_201
        resp.media = _to_json(self._repo.create(title=title))


class TodoItemResource:
    """Resource for GET /todos/{id}, PATCH /todos/{id}, DELETE /todos/{id}."""

    def __init__(self, repo: InMemoryTodoRepository) -> None:
        self._repo = repo

    def on_get(self, _req: falcon.Request, resp: falcon.Response, todo_id: int) -> None:
        try:
            todo = self._repo.get(todo_id)
        except KeyError:
            _error(resp, falcon.HTTP_404, "Todo not found")
            return
        resp.media = _to_json(todo)

    def on_patch(
        self, req: falcon.Request, resp: falcon.Response, todo_id: int
    ) -> None:
        body = _request_json(req)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            _error(resp, falcon.HTTP_422, "title must be a non-empty string")
            return
        try:
            todo = self._repo.update(todo_id, title=title, done=done)
        except KeyError:
            _error(resp, falcon.HTTP_404, "Todo not found")
            return
        resp.media = _to_json(todo)

    def on_delete(
        self, _req: falcon.Request, resp: falcon.Response, todo_id: int
    ) -> None:
        try:
            self._repo.delete(todo_id)
        except KeyError:
            _error(resp, falcon.HTTP_404, "Todo not found")
            return
        resp.status = falcon.HTTP_204


def create_app(repo: InMemoryTodoRepository | None = None) -> falcon.App:
    repo = repo or InMemoryTodoRepository()
    app = falcon.App()
    app.add_route("/todos", TodoCollectionResource(repo))
    app.add_route("/todos/{todo_id:int}", TodoItemResource(repo))
    return app


app = create_app()
