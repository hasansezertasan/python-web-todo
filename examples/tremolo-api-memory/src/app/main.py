"""Todo JSON API with Tremolo and in-memory storage."""

import json
import os

from tremolo import Application

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


async def _request_body(request) -> dict:
    try:
        raw = await request.body()
    except Exception:
        return {}
    if not raw:
        return {}
    try:
        body = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    return body if isinstance(body, dict) else {}


def _json(response, payload: object, status: int = 200, reason: str = "OK") -> str:
    response.set_status(status, reason)
    response.set_content_type("application/json")
    return json.dumps(payload)


def _not_found(response) -> str:
    return _json(response, {"error": "Todo not found"}, 404, "Not Found")


def _invalid_title(response) -> str:
    return _json(
        response,
        {"error": "title must be a non-empty string"},
        422,
        "Unprocessable Entity",
    )


def _parse_id(todo_id) -> int | None:
    if isinstance(todo_id, (bytes, bytearray)):
        todo_id = bytes(todo_id).decode("latin-1")
    try:
        return int(todo_id)
    except (TypeError, ValueError):
        return None


class TodosView:
    """Collection resource. Tremolo dispatches per HTTP method to get/post.

    Must stay module-level: Tremolo boots workers via multiprocessing
    (spawn), which pickles the app, so locally-defined classes fail to boot.
    The store arrives via route options into __init__ (Tremolo idiom).
    """

    def __init__(self, repo: InMemoryTodoRepository, **kwargs) -> None:
        self.repo = repo

    async def get(self, response, **server) -> str:
        return _json(response, [_to_json(todo) for todo in self.repo.list()])

    async def post(self, request, response, **server) -> str:
        title = (await _request_body(request)).get("title")
        if not _valid_title(title):
            return _invalid_title(response)
        return _json(response, _to_json(self.repo.create(title=title)), 201, "Created")


class TodoDetailView:
    """Item resource. The [^/]+ segment keeps non-numeric ids on this
    route so they 404 with a JSON body instead of Tremolo's default page."""

    def __init__(self, repo: InMemoryTodoRepository, **kwargs) -> None:
        self.repo = repo

    async def get(self, response, todo_id=b"", **server) -> str:
        parsed = _parse_id(todo_id)
        if parsed is None:
            return _not_found(response)
        try:
            todo = self.repo.get(parsed)
        except KeyError:
            return _not_found(response)
        return _json(response, _to_json(todo))

    async def patch(self, request, response, todo_id=b"", **server) -> str:
        parsed = _parse_id(todo_id)
        if parsed is None:
            return _not_found(response)
        body = await _request_body(request)
        title = body.get("title")
        done = body.get("done")
        if "title" in body and not _valid_title(title):
            return _invalid_title(response)
        try:
            todo = self.repo.update(parsed, title=title, done=done)
        except KeyError:
            return _not_found(response)
        return _json(response, _to_json(todo))

    async def delete(self, response, todo_id=b"", **server) -> bytes:
        parsed = _parse_id(todo_id)
        if parsed is None:
            return _not_found(response).encode()
        try:
            self.repo.delete(parsed)
        except KeyError:
            return _not_found(response).encode()
        response.set_status(204, "No Content")
        return b""


def create_app(repo: InMemoryTodoRepository | None = None) -> Application:
    """Build a fresh Tremolo Application with a fresh (or injected) store."""
    repo = repo or InMemoryTodoRepository()
    app = Application()
    app.route("/todos", repo=repo)(TodosView)
    app.route(r"^/todos/(?P<todo_id>[^/]+)$", repo=repo)(TodoDetailView)
    return app


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    app.run("0.0.0.0", port)


if __name__ == "__main__":
    main()
