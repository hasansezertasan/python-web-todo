"""Todo JSON API with Emmett and in-memory storage."""

import os
from pathlib import Path

from emmett import App, request, response
from emmett.tools import service

from .models import Todo
from .repository import InMemoryTodoRepository


def _item(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _invalid_title(title: object) -> bool:
    return not isinstance(title, str) or title == ""


def create_app(repo: InMemoryTodoRepository | None = None) -> App:
    """Return a fresh Emmett app with its own empty store (unless given)."""
    repo = repo or InMemoryTodoRepository()
    app = App(__name__)

    @app.route("/todos", methods="get")
    @service.json
    async def list_todos() -> list[dict]:
        return [_item(todo) for todo in repo.list()]

    @app.route("/todos", methods="post")
    @service.json
    async def create_todo() -> dict | None:
        payload = await request.body_params
        if _invalid_title(payload.title):
            response.status = 422
            return {"detail": "Title must be a non-empty string"}
        response.status = 201
        return _item(repo.create(title=payload.title))

    @app.route("/todos/<int:todo_id>", methods="get")
    @service.json
    async def get_todo(todo_id: int) -> dict | None:
        try:
            todo = repo.get(todo_id)
        except KeyError:
            response.status = 404
            return {"detail": "Todo not found"}
        return _item(todo)

    @app.route("/todos/<int:todo_id>", methods="patch")
    @service.json
    async def update_todo(todo_id: int) -> dict | None:
        payload = await request.body_params
        title = payload.title if "title" in payload else None
        done = payload.done if "done" in payload else None
        if "title" in payload and _invalid_title(title):
            response.status = 422
            return {"detail": "Title must be a non-empty string"}
        if "done" in payload and not isinstance(done, bool):
            response.status = 422
            return {"detail": "Done must be a boolean"}
        try:
            todo = repo.update(todo_id, title=title, done=done)
        except KeyError:
            response.status = 404
            return {"detail": "Todo not found"}
        return _item(todo)

    @app.route("/todos/<int:todo_id>", methods="delete")
    @service.json
    async def delete_todo(todo_id: int) -> None:
        try:
            repo.delete(todo_id)
        except KeyError:
            response.status = 404
            return {"detail": "Todo not found"}
        response.status = 204
        return None

    return app


app = create_app()


def main() -> None:
    import sys

    from granian import Granian

    port = int(os.environ.get("PORT", "8000"))
    # Allow running both from the example dir and from the repo root
    # (`uv run --project examples/emmett-api-memory python -m app.main` installs
    # the `app` package, but the installed target needs no cwd assumption;
    # resolve src/ from __file__ so the default never depends on cwd).
    src_dir = str(Path(__file__).resolve().parent.parent)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    server = Granian("app.main:app", interface="asgi", address="0.0.0.0", port=port)
    server.serve()


if __name__ == "__main__":
    main()
