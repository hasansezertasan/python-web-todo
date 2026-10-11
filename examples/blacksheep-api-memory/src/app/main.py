"""Todo JSON API with BlackSheep and in-memory storage."""

from dataclasses import dataclass

from blacksheep import Application, Request, Response, json
from blacksheep.server.openapi.v3 import OpenAPIHandler
from blacksheep.server.routing import Router
from openapidocs.v3 import Info

from .repository import InMemoryTodoRepository


@dataclass
class TodoRead:
    """Wire shape of a todo item; also feeds the OpenAPI item schema."""

    id: int
    title: str
    done: bool = False


def _not_found() -> Response:
    return json({"detail": "Todo not found"}, status=404)


def _unprocessable(detail: str) -> Response:
    # BlackSheep's model binders report invalid request bodies as 400 by
    # default; the shared JSON API contract expects 422, so this example
    # parses bodies manually and answers 422 here (same remap the Litestar
    # examples do via an exception handler).
    return json({"detail": detail}, status=422)


def _parse_id(raw: str) -> int | None:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) >= 1


def create_app(repo: InMemoryTodoRepository | None = None) -> Application:
    repo = repo or InMemoryTodoRepository()
    # A fresh Router per app: Application() would otherwise share the global
    # default router, so a second create_app() in the same process would
    # re-register every route (and crash on duplicates).
    app = Application(router=Router())
    docs = OpenAPIHandler(
        info=Info(title="Todo API (BlackSheep, in-memory)", version="0.1.0")
    )
    docs.bind_app(app)

    @app.router.get("/todos")
    async def list_todos() -> list[TodoRead]:
        """List all todos."""
        return [
            TodoRead(id=todo.id, title=todo.title, done=todo.done)
            for todo in repo.list()
        ]

    @app.router.post("/todos")
    async def create_todo(request: Request) -> Response:
        """Create a todo."""
        try:
            payload = await request.json()
        except Exception:
            return _unprocessable("Request body must be valid JSON")
        if not isinstance(payload, dict):
            return _unprocessable("Request body must be a JSON object")
        title = payload.get("title")
        if not _valid_title(title):
            return _unprocessable("title must be a non-empty string")
        todo = repo.create(title=title)
        return json(TodoRead(id=todo.id, title=todo.title, done=todo.done), status=201)

    @app.router.get("/todos/{todo_id}")
    async def get_todo(todo_id: str) -> Response:
        """Get one todo."""
        parsed = _parse_id(todo_id)
        if parsed is None:
            return _not_found()
        try:
            todo = repo.get(parsed)
        except KeyError:
            return _not_found()
        return json(TodoRead(id=todo.id, title=todo.title, done=todo.done))

    @app.router.patch("/todos/{todo_id}")
    async def update_todo(todo_id: str, request: Request) -> Response:
        """Update a todo's title and/or done flag."""
        parsed = _parse_id(todo_id)
        if parsed is None:
            return _not_found()
        try:
            payload = await request.json()
        except Exception:
            return _unprocessable("Request body must be valid JSON")
        if not isinstance(payload, dict):
            return _unprocessable("Request body must be a JSON object")
        title = payload.get("title", None)
        if "title" in payload and not _valid_title(title):
            return _unprocessable("title must be a non-empty string")
        done = payload.get("done", None)
        if "done" in payload and not isinstance(done, bool):
            return _unprocessable("done must be a boolean")
        try:
            todo = repo.update(parsed, title=title, done=done)
        except KeyError:
            return _not_found()
        return json(TodoRead(id=todo.id, title=todo.title, done=todo.done))

    @app.router.delete("/todos/{todo_id}")
    async def delete_todo(todo_id: str) -> Response:
        """Delete a todo."""
        parsed = _parse_id(todo_id)
        if parsed is None:
            return _not_found()
        try:
            repo.delete(parsed)
        except KeyError:
            return _not_found()
        return Response(204, None, None)

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
