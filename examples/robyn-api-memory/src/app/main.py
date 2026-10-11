"""Todo JSON API with Robyn and in-memory storage."""

import os

from robyn import Request, Response, Robyn, jsonify

from .models import Todo
from .repository import InMemoryTodoRepository
from .schemas import TodoRead

JSON_HEADERS = {"Content-Type": "application/json"}


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _body(request: Request) -> dict:
    try:
        data = request.json()
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _error(status_code: int, message: str) -> Response:
    return Response(status_code, JSON_HEADERS, jsonify({"detail": message}))


def _todo_id(request: Request) -> int | None:
    try:
        return int(request.path_params.get("id", ""))
    except (TypeError, ValueError):
        return None


def create_app(repo: InMemoryTodoRepository | None = None) -> Robyn:
    repo = repo or InMemoryTodoRepository()
    app = Robyn(__file__)

    @app.get("/todos", response_model=list[TodoRead])
    async def list_todos(request: Request) -> list[dict]:
        return [_to_json(todo) for todo in repo.list()]

    @app.post("/todos", status_code=201, response_model=TodoRead)
    async def create_todo(request: Request) -> dict | Response:
        title = _body(request).get("title")
        if not _valid_title(title):
            return _error(422, "title must be a non-empty string")
        return _to_json(repo.create(title=title))

    @app.get("/todos/:id", response_model=TodoRead)
    async def get_todo(request: Request) -> dict | Response:
        todo_id = _todo_id(request)
        if todo_id is None:
            return _error(404, "Todo not found")
        try:
            return _to_json(repo.get(todo_id))
        except KeyError:
            return _error(404, "Todo not found")

    @app.patch("/todos/:id", response_model=TodoRead)
    async def update_todo(request: Request) -> dict | Response:
        todo_id = _todo_id(request)
        if todo_id is None:
            return _error(404, "Todo not found")
        body = _body(request)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return _error(422, "title must be a non-empty string")
        if done is not None and not isinstance(done, bool):
            return _error(422, "done must be a boolean")
        try:
            return _to_json(repo.update(todo_id, title=title, done=done))
        except KeyError:
            return _error(404, "Todo not found")

    @app.delete("/todos/:id", status_code=204)
    async def delete_todo(request: Request) -> Response:
        todo_id = _todo_id(request)
        if todo_id is None:
            return _error(404, "Todo not found")
        try:
            repo.delete(todo_id)
        except KeyError:
            return _error(404, "Todo not found")
        return Response(204, JSON_HEADERS, "")

    return app


app = create_app()


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    app.start(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
