"""Todo JSON API with Klein (Twisted micro-framework) and in-memory storage."""

import json
import os

from klein import Klein

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _request_body(request) -> dict:
    try:
        raw = request.content.read()
        body = json.loads(raw.decode("utf-8")) if raw else {}
    except (ValueError, UnicodeDecodeError):
        return {}
    return body if isinstance(body, dict) else {}


def _json(request, payload: object, status: int = 200):
    request.setHeader("Content-Type", "application/json")
    request.setResponseCode(status)
    return json.dumps(payload)


def _not_found(request):
    return _json(request, {"error": "Todo not found"}, 404)


def _parse_id(request, raw_id: str) -> int | None:
    try:
        return int(raw_id)
    except (TypeError, ValueError):
        return None


def create_app(repo: InMemoryTodoRepository | None = None) -> Klein:
    """Build a fresh Klein app (routes + store) per call."""
    repo = repo or InMemoryTodoRepository()
    app = Klein()

    @app.route("/todos", methods=["GET"])
    def list_todos(request):
        return _json(request, [_to_json(todo) for todo in repo.list()])

    @app.route("/todos", methods=["POST"])
    def create_todo(request):
        title = _request_body(request).get("title")
        if not _valid_title(title):
            return _json(request, {"error": "title must be a non-empty string"}, 422)
        return _json(request, _to_json(repo.create(title=title)), 201)

    @app.route("/todos/<todo_id>", methods=["GET"])
    def get_todo(request, todo_id: str):
        parsed = _parse_id(request, todo_id)
        if parsed is None:
            return _not_found(request)
        try:
            todo = repo.get(parsed)
        except KeyError:
            return _not_found(request)
        return _json(request, _to_json(todo))

    @app.route("/todos/<todo_id>", methods=["PATCH"])
    def update_todo(request, todo_id: str):
        parsed = _parse_id(request, todo_id)
        if parsed is None:
            return _not_found(request)
        body = _request_body(request)
        title = body.get("title")
        done = body.get("done")
        if "title" in body and not _valid_title(title):
            return _json(request, {"error": "title must be a non-empty string"}, 422)
        try:
            todo = repo.update(parsed, title=title, done=done)
        except KeyError:
            return _not_found(request)
        return _json(request, _to_json(todo))

    @app.route("/todos/<todo_id>", methods=["DELETE"])
    def delete_todo(request, todo_id: str):
        parsed = _parse_id(request, todo_id)
        if parsed is None:
            return _not_found(request)
        try:
            repo.delete(parsed)
        except KeyError:
            return _not_found(request)
        request.setResponseCode(204)
        return b""

    return app


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    create_app().run("0.0.0.0", port)


if __name__ == "__main__":
    main()
