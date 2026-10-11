"""Todo JSON API with Sanic and in-memory storage."""

import itertools

from sanic import Request, Sanic
from sanic.response import HTTPResponse, empty, json

from .models import Todo
from .repository import InMemoryTodoRepository

# Sanic keeps a process-wide registry keyed by app name and refuses duplicate
# names, so each factory call mints a distinct name. State isolation still
# comes from the fresh repository per call.
_app_names = itertools.count(1)


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def _body(request: Request) -> dict:
    try:
        data = request.json
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def create_app(repo: InMemoryTodoRepository | None = None) -> Sanic:
    repo = repo or InMemoryTodoRepository()
    app = Sanic(f"todo-api-{next(_app_names)}")
    app.ctx.repo = repo

    @app.get("/todos")
    async def list_todos(request: Request) -> HTTPResponse:
        return json([_to_json(todo) for todo in repo.list()])

    @app.post("/todos")
    async def create_todo(request: Request) -> HTTPResponse:
        title = _body(request).get("title")
        if not _valid_title(title):
            return json({"error": "title must be a non-empty string"}, status=422)
        return json(_to_json(repo.create(title=title)), status=201)

    @app.get("/todos/<todo_id:int>")
    async def get_todo(request: Request, todo_id: int) -> HTTPResponse:
        try:
            return json(_to_json(repo.get(todo_id)))
        except KeyError:
            return json({"error": "Todo not found"}, status=404)

    @app.patch("/todos/<todo_id:int>")
    async def update_todo(request: Request, todo_id: int) -> HTTPResponse:
        body = _body(request)
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return json({"error": "title must be a non-empty string"}, status=422)
        try:
            return json(_to_json(repo.update(todo_id, title=title, done=done)))
        except KeyError:
            return json({"error": "Todo not found"}, status=404)

    @app.delete("/todos/<todo_id:int>")
    async def delete_todo(request: Request, todo_id: int) -> HTTPResponse:
        try:
            repo.delete(todo_id)
        except KeyError:
            return json({"error": "Todo not found"}, status=404)
        return empty(status=204)

    return app


app = create_app()


def main() -> None:
    app.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
