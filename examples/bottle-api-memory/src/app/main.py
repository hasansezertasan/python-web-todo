"""Todo JSON API with Bottle and in-memory storage."""

import json
import os

from bottle import Bottle, request, response

from .models import Todo
from .repository import InMemoryTodoRepository


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _json_body(payload: object, status: int = 200) -> str:
    response.content_type = "application/json"
    response.status = status
    return json.dumps(payload)


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _request_body() -> dict:
    try:
        body = request.json
    except Exception:
        return {}
    return body if isinstance(body, dict) else {}


def create_app(repo: InMemoryTodoRepository | None = None) -> Bottle:
    repo = repo or InMemoryTodoRepository()
    app = Bottle()

    @app.get("/todos")
    def list_todos():
        return _json_body([_to_json(todo) for todo in repo.list()])

    @app.post("/todos")
    def create_todo():
        title = _request_body().get("title")
        if not _valid_title(title):
            return _json_body({"error": "title must be a non-empty string"}, 422)
        return _json_body(_to_json(repo.create(title=title)), 201)

    @app.get("/todos/<todo_id:int>")
    def get_todo(todo_id: int):
        try:
            todo = repo.get(todo_id)
        except KeyError:
            return _json_body({"error": "Todo not found"}, 404)
        return _json_body(_to_json(todo))

    @app.patch("/todos/<todo_id:int>")
    def update_todo(todo_id: int):
        body = _request_body()
        title = body.get("title")
        done = body.get("done")
        if "title" in body and not _valid_title(title):
            return _json_body({"error": "title must be a non-empty string"}, 422)
        try:
            todo = repo.update(todo_id, title=title, done=done)
        except KeyError:
            return _json_body({"error": "Todo not found"}, 404)
        return _json_body(_to_json(todo))

    @app.delete("/todos/<todo_id:int>")
    def delete_todo(todo_id: int):
        try:
            repo.delete(todo_id)
        except KeyError:
            return _json_body({"error": "Todo not found"}, 404)
        response.status = 204
        return ""

    return app


app = create_app()


def main() -> None:
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
