"""Todo JSON API with Clastic and in-memory storage."""

import json
from typing import Any

from clastic import DELETE, GET, POST, Application, Response, render_json
from clastic.route import PATCH

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _read_json_body(request: Any) -> dict:
    try:
        raw = request.get_data(as_text=True)
    except Exception:
        return {}
    if not raw:
        return {}
    try:
        body = json.loads(raw)
    except ValueError:
        return {}
    return body if isinstance(body, dict) else {}


def _json_response(data: dict, status: int) -> Response:
    return Response(json.dumps(data), status=status, content_type="application/json")


def _not_found() -> Response:
    return _json_response({"error": "Todo not found"}, 404)


def _parse_id(todo_id: str) -> int | None:
    try:
        return int(todo_id)
    except (TypeError, ValueError):
        return None


def list_todos(store: InMemoryTodoRepository) -> list[dict]:
    return [_to_json(todo) for todo in store.list()]


def create_todo(request: Any, store: InMemoryTodoRepository) -> Response:
    body = _read_json_body(request)
    title = body.get("title")
    if not _valid_title(title):
        return _json_response({"error": "title must be a non-empty string"}, 422)
    return _json_response(_to_json(store.create(title=title)), 201)


def get_todo(store: InMemoryTodoRepository, todo_id: str) -> dict | Response:
    parsed_id = _parse_id(todo_id)
    if parsed_id is None:
        return _not_found()
    try:
        return _to_json(store.get(parsed_id))
    except KeyError:
        return _not_found()


def update_todo(
    request: Any, store: InMemoryTodoRepository, todo_id: str
) -> dict | Response:
    parsed_id = _parse_id(todo_id)
    if parsed_id is None:
        return _not_found()
    body = _read_json_body(request)
    title = body.get("title")
    done = body.get("done")
    if title is not None and not _valid_title(title):
        return _json_response({"error": "title must be a non-empty string"}, 422)
    if done is not None and not isinstance(done, bool):
        return _json_response({"error": "done must be a boolean"}, 422)
    try:
        return _to_json(store.update(parsed_id, title=title, done=done))
    except KeyError:
        return _not_found()


def delete_todo(store: InMemoryTodoRepository, todo_id: str) -> Response:
    parsed_id = _parse_id(todo_id)
    if parsed_id is None:
        return _not_found()
    try:
        store.delete(parsed_id)
    except KeyError:
        return _not_found()
    return Response("", status=204)


def create_app(repo: InMemoryTodoRepository | None = None) -> Application:
    store = repo or InMemoryTodoRepository()
    routes = [
        GET("/todos", list_todos, render_json),
        POST("/todos", create_todo),
        GET("/todos/<todo_id>", get_todo, render_json),
        PATCH("/todos/<todo_id>", update_todo, render_json),
        DELETE("/todos/<todo_id>", delete_todo),
    ]
    return Application(routes, resources={"store": store})


app = create_app()


def main() -> None:
    app.serve(address="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
